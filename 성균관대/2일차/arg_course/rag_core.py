# brute-force : 완전탐색 알고리즘. 즉, 가능한 모든 경우의 수를 모두 탐색하면서 요구조건에 충족되는 결과 from __future__ import annotations
### 의도: 임베딩 기반 검색의 핵심 로직(임베딩 생성 → 유사도 계산 → top-k 선택)과, evidence 기반 답변 생성을 담당한다.
### 검색: FAISS 없이도 임베딩 벡터를 정규화한 뒤, 코사인 유사도(내적)로 후보를 점수화하여 top-k를 선택한다.
### 품질개선(옵션): Query rewrite로 검색 질의를 정리하고, MMR로 중복을 줄이며, LLM rerank로 “직접 답하는 근거” 순으로 재정렬한다.
### 답변: 선택된 근거를 citation([source|p?|c?]) 형태로 제공하여, 답변이 근거에 연결되도록 강제한다.

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional
import os
import json

import numpy as np
from openai import OpenAI

# =========================================
# 모델/설정
# =========================================
# 임베딩 모델: 텍스트를 벡터(의미 표현)로 변환하는 데 사용
EMBED_MODEL = "text-embedding-3-small"

# 채팅 모델: (1) 질의 리라이트, (2) LLM 기반 rerank, (3) 최종 답변 생성에 사용
# ※ ChatCompletions API를 사용하는 구버전 스타일 모델명
CHAT_MODEL = "gpt-4-0613"


def get_client() -> OpenAI:
    """
    환경변수 OPENAI_API_KEY로 OpenAI 클라이언트를 생성한다.

    Raises:
        RuntimeError: OPENAI_API_KEY가 설정되어 있지 않으면 예외 발생.
    """
    key = os.getenv("OPENAI_API_KEY") or ""
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=key)


def embed_texts(client: OpenAI, texts: List[str]) -> np.ndarray:
    """
    여러 개 텍스트를 임베딩 벡터로 변환하여 (N, d) numpy 배열로 반환한다.

    - resp.data 안에 각 텍스트의 embedding 벡터가 들어있다.
    - float32로 변환해 메모리 사용량을 줄이고 dot product를 빠르게 계산한다.
    """
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    vecs = np.array([d.embedding for d in resp.data], dtype=np.float32)
    return vecs


def _normalize_rows(mat: np.ndarray) -> np.ndarray:
    """
    행(row) 단위 L2 정규화.
    - 각 벡터를 길이 1로 만들어 코사인 유사도 계산을 dot product로 대체 가능하게 한다.
    - 1e-12는 0으로 나누는 문제를 방지한다.
    """
    denom = np.linalg.norm(mat, axis=1, keepdims=True) + 1e-12
    return mat / denom


def _normalize(vec: np.ndarray) -> np.ndarray:
    """
    단일 벡터 L2 정규화.
    - 코사인 유사도 계산을 위해 길이를 1로 맞춘다.
    """
    return vec / (np.linalg.norm(vec) + 1e-12)


@dataclass
class VectorIndex:
    """
    매우 단순한 벡터 인덱스 구조.

    vectors:
        (N, d) 형태의 정규화된 임베딩 행렬. (코사인 유사도용)
    chunks:
        각 청크의 원문과 메타데이터를 담는 리스트.
        예: [{"text": "...", "meta": {"source": "...", "page": 1, "chunk_id": 3}}, ...]
    """
    vectors: np.ndarray                 # (N, d) normalized
    chunks: List[Dict[str, Any]]        # [{"text":..., "meta":...}]


def build_index(client: OpenAI, chunks: List[Dict[str, Any]]) -> VectorIndex:
    """
    chunks로부터 임베딩을 생성하고 정규화한 뒤 VectorIndex를 만든다.

    흐름:
    1) chunks의 text만 추출
    2) 임베딩 생성 (N, d)
    3) 행 단위 정규화
    4) vectors + chunks를 묶어 인덱스 반환
    """
    texts = [c["text"] for c in chunks]
    vecs = embed_texts(client, texts)
    vecs = _normalize_rows(vecs)
    return VectorIndex(vectors=vecs, chunks=chunks)


# -----------------------
# Query rewrite (검색용으로 질문을 짧게 정리)
# -----------------------
def rewrite_query(client: OpenAI, query: str) -> str:
    """
    사용자의 질문(query)을 '검색에 적합한 짧은 쿼리'로 변환한다.

    목적:
    - 사용자 질문은 장황하거나 불필요한 말이 포함될 수 있음
    - 리라이트로 핵심 키워드/제약조건을 남겨 retrieval 품질을 올리려는 의도

    주의:
    - '답변'이 아니라 검색용 문장(한 줄)만 내도록 강제한다.
    """
    prompt = f"""
You rewrite user questions into a SHORT search query for retrieval.
Rules:
- Keep key entities/constraints/technical terms.
- Remove filler. Output ONE line only.
- Do not answer the question.

User question:
{query}

Search query:
""".strip()

    r = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,   # 결정적으로(재현성 있게) 리라이트
        max_tokens=64,     # 한 줄 짧은 출력이 목적
    )
    out = r.choices[0].message.content.strip()

    # 혹시 빈 문자열이 나오면 원래 query를 그대로 사용
    return out if out else query


# -----------------------
# MMR selection (브루트포스 결과에서도 다양성 확보)
# -----------------------
def _mmr_select(
    qvec: np.ndarray,           # [d] 정규화된 쿼리 벡터
    cand_ids: List[int],        # 후보 문서/청크 인덱스 리스트
    vectors: np.ndarray,        # [N, d] 정규화된 전체 벡터 행렬
    k: int,                     # 최종 선택 개수
    lambda_mult: float = 0.5    # 관련성 vs 다양성 트레이드오프(0~1)
) -> List[int]:
    """
    MMR(Maximal Marginal Relevance)로 top-k를 고른다.

    아이디어:
    - 단순 top-k는 비슷한 내용이 여러 개 뽑힐 수 있음
    - MMR은 "쿼리와의 관련성(rel)"은 높이고,
      이미 뽑힌 것들과의 유사도(div; 중복)"는 낮춰 다양성을 확보한다.

    점수:
      mmr = λ * rel - (1-λ) * div
    - λ가 1에 가까우면 '관련성' 위주(그냥 top-k와 비슷)
    - λ가 0에 가까우면 '다양성' 위주(중복을 더 강하게 억제)
    """
    selected: List[int] = []
    remaining = cand_ids.copy()

    # q_sims: 후보 각각에 대해 쿼리와의 유사도(코사인=dot product)를 미리 계산
    q_sims = {i: float(np.dot(qvec, vectors[i])) for i in remaining}

    while remaining and len(selected) < k:
        best_id, best_val = None, -1e9

        for cid in remaining:
            # rel: 쿼리-후보 관련성
            rel = q_sims[cid]

            # div: 이미 선택된 청크들과의 최대 유사도(중복 정도)
            div = 0.0 if not selected else max(
                float(np.dot(vectors[cid], vectors[sid])) for sid in selected
            )

            mmr = lambda_mult * rel - (1.0 - lambda_mult) * div

            if mmr > best_val:
                best_val, best_id = mmr, cid

        selected.append(best_id)
        remaining.remove(best_id)

    return selected


# -----------------------
# LLM rerank (LLM에게 후보들 중 무엇이 질문에 더 직접 답인지 재정렬)
# -----------------------
def rerank_llm(client: OpenAI, query: str, candidates: List[Dict[str, Any]], top_k: int) -> List[int]:
    """
    candidates(청크들)를 LLM에게 보여주고 "질문에 가장 직접적인 것" 순으로 재정렬한다.

    반환:
    - candidates 리스트의 인덱스(0..len-1)를 ranked 형태로 반환
    - 실패 시 안전하게 [0,1,2,...] 기본 순서를 반환

    주의:
    - 비용/지연이 늘어날 수 있다(후보 텍스트를 LLM에 보내므로).
    - text를 1200자까지만 자르는 이유는 컨텍스트/비용 관리 목적.
    """
    items = []
    for i, c in enumerate(candidates):
        meta = c.get("meta", {})
        # 출처 문자열 구성(있으면 source, 없으면 url, 그것도 없으면 unknown)
        src = meta.get("source") or meta.get("url") or "unknown"
        page = meta.get("page", "")
        cid = meta.get("chunk_id", "")

        items.append({
            "i": i,
            "source": src,
            "page": page,
            "chunk_id": cid,
            "text": c.get("text", "")[:1200],  # 너무 길면 비용 증가 → 일부만 사용
        })

    prompt = f"""
You are a reranker. Rank candidates by how directly they answer the question.
Return JSON only: {{"ranked":[0,1,2,...]}}.

Question:
{query}

Candidates (JSON):
{json.dumps(items, ensure_ascii=False)}
""".strip()

    r = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,  # 재정렬은 결정적으로
        max_tokens=256,   # ranked 배열만 받으면 충분
    )
    out = r.choices[0].message.content.strip()

    # LLM 출력이 JSON이 아닐 수도 있으므로 try/except로 방어
    try:
        ranked = json.loads(out).get("ranked", [])
        ranked = [i for i in ranked if isinstance(i, int)]
        if ranked:
            return ranked[:top_k]
    except Exception:
        pass

    # 실패 시 기본 순서(앞에서부터 top_k)
    return list(range(min(top_k, len(candidates))))


def _cite(meta: Dict[str, Any]) -> str:
    """
    메타데이터(meta)로부터 인용 표기 문자열을 만든다.
    형식 예: [source|p3|c12]
    - source 또는 url 기반
    - page, chunk_id가 있으면 함께 표기
    """
    src = meta.get("source") or meta.get("url") or "unknown"
    page = meta.get("page", "")
    cid = meta.get("chunk_id", "")

    parts = [str(src)]
    if page != "":
        parts.append(f"p{page}")
    if cid != "":
        parts.append(f"c{cid}")
    return "[" + "|".join(parts) + "]"


# -----------------------
# Retrieval: brute-force + 옵션(rewrite/MMR/rerank)
# -----------------------
def retrieve(
    client: OpenAI,
    index: VectorIndex,
    query: str,
    top_k: int = 4,
    fetch_k: Optional[int] = None,
    use_rewrite: bool = True,
    use_mmr: bool = True,
    mmr_lambda: float = 0.5,
    use_rerank: bool = True,
) -> Tuple[str, List[Tuple[Dict[str, Any], float]]]:
    """
    브루트포스(전체 벡터 dot product) 기반 retrieval.

    절차:
    1) (옵션) query rewrite → search_query 생성
    2) search_query 임베딩 → qv 정규화
    3) 모든 청크와의 점수(scores = vectors @ qv) 계산
    4) 상위 fk개 후보(cand_ids) 선별 (fetch_k 또는 기본값)
    5) (옵션) MMR로 top_k개 선택
    6) (옵션) LLM rerank로 top_k 내부 순서를 재정렬
    7) (search_query, [(chunk, score), ...]) 반환

    반환의 search_query는 UI/로그에서 "리라이트가 무엇이었는지" 보여줄 때 유용.
    """
    # (1) 검색용으로 질의를 짧게 정리(옵션)
    search_query = rewrite_query(client, query) if use_rewrite else query

    # (2) 검색 질의 임베딩 (1개) → qv 정규화
    qv = embed_texts(client, [search_query])[0]
    qv = _normalize(qv)

    # (3) 전체 문서와의 코사인 유사도(=정규화된 벡터끼리 dot product)
    scores = index.vectors @ qv  # (N,)

    # (4) 후보 수 fk 결정
    # - fetch_k를 지정하지 않으면: top_k*4 또는 20 중 큰 값(최소 20개 후보 확보)
    fk = fetch_k if fetch_k is not None else max(top_k * 4, 20)
    fk = min(fk, len(scores))  # 문서 수보다 크게 잡히면 안 됨

    # 점수 내림차순 상위 fk개 후보 인덱스
    cand_ids = np.argsort(-scores)[:fk].tolist()

    # (5) top_k 선택: MMR 사용 여부에 따라 결정
    if use_mmr and len(cand_ids) > top_k:
        picked_ids = _mmr_select(
            qv,
            cand_ids,
            index.vectors,
            k=top_k,
            lambda_mult=mmr_lambda
        )
    else:
        picked_ids = cand_ids[:top_k]

    # 선택된 청크와 점수 묶기
    picked = [(index.chunks[i], float(scores[i])) for i in picked_ids]

    # (6) LLM rerank: top_k 후보들 사이의 순서만 재정렬
    if use_rerank and len(picked) > 1:
        cand_chunks = [c for (c, _) in picked]
        order = rerank_llm(client, query, cand_chunks, top_k=len(cand_chunks))
        picked = [picked[i] for i in order]

    # (7) 최종 반환
    return search_query, picked


def answer_with_rag(client: OpenAI, query: str, retrieved: List[Tuple[Dict[str, Any], float]]) -> str:
    """
    Retrieval 결과(retrieved)를 evidence로 넣어 최종 답변을 생성한다.

    핵심 정책:
    - "증거(evidence)만 사용"하도록 프롬프트로 강제
    - 근거가 부족하면 부족한 점을 말하고 '명확화 질문 1개'를 하도록 강제
    - 최종 답변에는 반드시 [source|p?|c?] 형태로 인용을 남기도록 강제

    출력 형식:
    1) Evidence summary (3-6 bullets)
    2) Final answer (concise, with citations)
    """
    blocks = []
    for i, (ch, score) in enumerate(retrieved, start=1):
        # 각 청크를 (인용표기 + 점수 + 텍스트) 형태로 묶어 evidence를 만든다.
        blocks.append(
            f"[{i}] {_cite(ch.get('meta', {}))} (score={score:.3f})\n{ch.get('text','')}"
        )
    evidence = "\n\n".join(blocks)

    prompt = f"""
You are a RAG assistant. Use ONLY the provided evidence.
If evidence is insufficient, say what is missing and ask one clarifying question.
You MUST cite sources in the final answer using [source|p?|c?].

Question:
{query}

Evidence:
{evidence}

Write:
1) Evidence summary (3-6 bullets)
2) Final answer (concise, with citations)
""".strip()

    r = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role":"user","content":prompt}],
        temperature=0.2,   # 답변은 약간의 자연스러움 허용(단, evidence 제약은 프롬프트가 담당)
        max_tokens=700,    # 요약+답변이 들어갈 만큼 충분히
    )
    return r.choices[0].message.content.strip()
