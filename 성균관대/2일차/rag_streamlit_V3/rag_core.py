# rag_core.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional
import os
import json

import numpy as np
import faiss
from openai import OpenAI

# -----------------------
# 모델 설정
# -----------------------
# - 임베딩 모델: chunk/text를 벡터로 바꿔 FAISS 검색에 사용합니다.
# - 채팅 모델: query rewrite, rerank, 최종 답변 생성에 사용합니다.
# - 실습 3단계는 Chroma 없이 FAISS(IndexFlatIP)만 유지합니다.
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4-0613"


def get_client() -> OpenAI:
    """
    환경변수 OPENAI_API_KEY로 OpenAI 클라이언트를 생성한다.

    Raises:
        RuntimeError: OPENAI_API_KEY가 설정되어 있지 않으면 예외 발생

    Notes:
        - app.py에서 UI로 받은 키를 os.environ에 주입해 두면 여기서 그대로 읽는다.
        - 임베딩/리라이트/리랭크/답변 생성까지 동일 client를 공유하는 구조를 전제로 한다.
    """
    # - 환경변수 OPENAI_API_KEY를 읽어 OpenAI 클라이언트를 만듭니다.
    # - 키가 없으면 즉시 예외를 내서 실습 중 원인 파악이 쉬워집니다.
    # - 이후 임베딩/리라이트/리랭크/답변 생성에서 같은 client를 공유합니다.
    key = os.getenv("OPENAI_API_KEY") or ""
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=key)


def embed_texts(client: OpenAI, texts: List[str]) -> np.ndarray:
    """
    텍스트 리스트를 임베딩 벡터로 변환하고, FAISS cosine 검색을 위해 L2 정규화한다.

    Args:
        client: OpenAI 클라이언트
        texts: 임베딩할 텍스트 리스트

    Returns:
        np.ndarray:
            shape (N, d), dtype float32
            각 row는 L2 정규화되어 있어 IndexFlatIP의 내적이 cosine 유사도가 된다.

    Notes:
        - OpenAI embeddings 응답(resp.data)에서 embedding만 뽑아 numpy 배열로 만든다.
        - faiss.normalize_L2는 행(row) 단위로 정규화한다.
    """
    # - 텍스트 리스트를 임베딩 API로 벡터화합니다.
    # - IndexFlatIP에서 cosine 유사도처럼 쓰기 위해 L2 정규화를 합니다.
    # - 반환 shape은 [N, d], dtype은 float32로 FAISS와 호환됩니다.
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    vecs = np.array([d.embedding for d in resp.data], dtype=np.float32)
    faiss.normalize_L2(vecs)
    return vecs


@dataclass
class VectorIndex:
    """
    Retrieval에 필요한 데이터를 묶어 보관하는 인덱스 컨테이너.

    Fields:
        index:
            FAISS 인덱스(여기서는 IndexFlatIP). 빠른 top-k 검색용.
        chunks:
            검색 결과를 원문/메타로 복원하기 위한 chunk 리스트.
            각 chunk는 {"text":..., "meta":...} 형태를 기대.
        vectors:
            전체 벡터를 저장해 MMR의 다양성(중복 억제) 계산에 사용.
            shape (N, d), L2 정규화된 상태.
    """
    # - index: FAISS 인덱스(내적 기반)로 빠른 top-k 검색을 수행합니다.
    # - chunks: 검색 결과를 원문/메타로 복원하기 위한 {"text","meta"} 리스트입니다.
    # - vectors: 전체 벡터를 저장해 MMR의 “다양성(중복 억제)” 계산에 씁니다.
    index: faiss.Index
    chunks: List[Dict[str, Any]]   # {"text":..., "meta":...}
    vectors: np.ndarray            # normalized vectors [N, d] for MMR


def build_faiss_index(client: OpenAI, chunks: List[Dict[str, Any]]) -> VectorIndex:
    """
    chunk(dict{text/meta}) 리스트로부터 임베딩을 만들고 FAISS(IndexFlatIP) 인덱스를 구성한다.

    Args:
        client: OpenAI 클라이언트
        chunks: [{"text": "...", "meta": {...}}, ...]

    Returns:
        VectorIndex: (index + chunks + vectors)

    Steps:
        1) chunks에서 text만 추출
        2) 임베딩 생성 + L2 정규화
        3) IndexFlatIP 생성 후 add(vecs)
        4) vecs를 vectors로 보관(MMR 계산용)
    """
    # - chunks의 text를 임베딩하고 FAISS(IndexFlatIP) 인덱스를 생성합니다.
    # - 벡터 정규화가 되어 있어 내적(IP)이 곧 cosine 유사도 역할을 합니다.
    # - 인덱스+chunks+vectors를 묶어 Retrieval 파이프라인에서 재사용합니다.
    texts = [c["text"] for c in chunks]
    vecs = embed_texts(client, texts)
    dim = vecs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(vecs)
    return VectorIndex(index=index, chunks=chunks, vectors=vecs)


# -----------------------
# 3-1) Query rewrite
# -----------------------
def rewrite_query(client: OpenAI, query: str) -> str:
    """
    사용자 질문을 검색에 유리한 '짧은 검색용 질의'로 재작성한다.

    목적:
        - 질문의 군더더기를 제거하고 핵심 키워드/제약/기술 용어를 남겨
          retrieval 성능을 안정화한다.

    출력 규칙:
        - 한 줄(one line)만 출력
        - 질문에 답하지 말 것

    Returns:
        리라이트된 검색 질의 문자열 (비어 있으면 원 query 반환)
    """
    # - 사용자 질문을 “검색에 유리한 짧은 질의”로 재작성합니다.
    # - 핵심 엔티티/제약/기술 용어는 유지하고 군더더기는 제거합니다.
    # - 답을 만들지 말고 한 줄만 출력하도록 규칙을 고정합니다.
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
        temperature=0.0,
        max_tokens=64,
    )
    out = r.choices[0].message.content.strip()
    return out if out else query


# -----------------------
# 3-2) MMR selection
# -----------------------
def _mmr_select(
    qvec: np.ndarray,            # [d] normalized
    cand_ids: List[int],
    vectors: np.ndarray,         # [N, d] normalized
    k: int,
    lambda_mult: float = 0.5
) -> List[int]:
    """
    MMR(Maximal Marginal Relevance)로 후보를 선택한다.

    목적:
        - 단순 top-k는 비슷한 chunk가 여러 개 뽑히는 경우가 많다.
        - MMR은 "관련성(rel)"과 "다양성(div)"을 함께 고려하여
          질문에 유용하면서도 중복이 적은 근거 세트를 만든다.

    점수:
        mmr = lambda_mult * rel - (1 - lambda_mult) * div
        - rel: query와 후보 chunk의 유사도
        - div: 이미 선택된 chunk들과 후보 chunk의 최대 유사도(중복 정도)

    Args:
        qvec: 질의 벡터(정규화된 1개 벡터)
        cand_ids: FAISS에서 뽑은 후보 인덱스 리스트
        vectors: 전체 chunk 벡터(정규화됨)
        k: 최종 선택 개수
        lambda_mult: 관련성-다양성 균형(1에 가까울수록 관련성 우선)

    Returns:
        선택된 chunk 인덱스 리스트(길이 <= k)
    """
    # - MMR은 “관련성”과 “다양성”을 함께 고려해 후보를 고릅니다.
    # - q에 가까우면서도 이미 뽑힌 chunk와 너무 비슷하면 패널티를 줍니다.
    # - lambda_mult↑: 관련성 우선, lambda_mult↓: 다양성(중복 억제) 우선입니다.
    selected: List[int] = []
    remaining = cand_ids.copy()

    # query와 후보의 유사도 미리 계산(속도 개선)
    q_sims = {i: float(np.dot(qvec, vectors[i])) for i in remaining}

    while remaining and len(selected) < k:
        best_id = None
        best_val = -1e9

        for cid in remaining:
            rel = q_sims[cid]

            # div: 이미 고른 것들과의 최대 유사도(가장 비슷한 정도)
            if not selected:
                div = 0.0
            else:
                div = max(float(np.dot(vectors[cid], vectors[sid])) for sid in selected)

            mmr = lambda_mult * rel - (1.0 - lambda_mult) * div
            if mmr > best_val:
                best_val = mmr
                best_id = cid

        selected.append(best_id)
        remaining.remove(best_id)

    return selected


# -----------------------
# 3-3) LLM rerank
# -----------------------
def rerank_llm(
    client: OpenAI,
    query: str,
    candidates: List[Dict[str, Any]],
    top_k: int
) -> List[int]:
    """
    LLM을 이용해 후보 chunk를 "질문에 직접 답하는 정도" 기준으로 재정렬한다.

    아이디어:
        - 벡터 유사도는 '비슷한 주제'를 찾는 데는 강하지만,
          "질문에 직접 답이 되는 문장"인지까지는 약할 수 있다.
        - 후보 수가 적을 때(예: top_k~fetch_k 범위) LLM rerank로 품질을 올릴 수 있다.

    출력 규칙:
        - 모델은 JSON만 반환: {"ranked":[0,1,2,...]}
        - ranked는 candidates의 인덱스를 의미

    안정성:
        - 모델 출력이 깨지거나 중복/범위 밖 인덱스가 있으면
          _normalize()로 안전한 순열로 보정하여 앱이 죽지 않게 한다.

    Returns:
        rerank된 후보 인덱스 리스트(길이 <= top_k)
    """
    # - 후보 chunk들을 “질문에 직접 답하는 정도” 기준으로 다시 정렬합니다.
    # - 모델은 순서만 JSON({"ranked":[...]})으로 반환하고, 내용 생성은 하지 않습니다.
    # - 출력이 깨져도 앱이 죽지 않도록 인덱스 리스트를 정규화(permutation)합니다.
    items = []
    for i, c in enumerate(candidates):
        meta = c.get("meta", {})
        src = meta.get("source") or meta.get("url") or "unknown"
        page = meta.get("page", "")
        cid = meta.get("chunk_id", "")
        items.append({
            "i": i,
            "source": src,
            "page": page,
            "chunk_id": cid,
            "text": (c.get("text", "")[:1200]),  # 너무 길면 비용/노이즈 증가 → 상한
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
        temperature=0.0,
        max_tokens=256,
    )
    out = r.choices[0].message.content.strip()

    def _normalize(order: List[int], n: int) -> List[int]:
        """
        LLM이 준 ranked 리스트를 안전한 순열로 정규화한다.

        처리:
            - int가 아니거나 0..n-1 범위를 벗어나면 제거
            - 중복 인덱스 제거
            - 누락된 인덱스는 원래 순서대로 뒤에 추가
            -> 항상 길이 n인 순열을 반환

        Args:
            order: LLM 출력 ranked 리스트
            n: 후보 개수

        Returns:
            길이 n의 안전한 인덱스 순열
        """
        # - 0..n-1 범위 밖/중복 인덱스를 제거해 안전한 순열을 만듭니다.
        # - 빠진 항목은 원래 순서대로 뒤에 채워 항상 길이 n을 보장합니다.
        # - 이렇게 하면 rerank 결과가 깨져도 IndexError 없이 동작합니다.
        seen = set()
        cleaned: List[int] = []
        for x in order:
            if isinstance(x, int) and 0 <= x < n and x not in seen:
                cleaned.append(x)
                seen.add(x)
        for i in range(n):
            if i not in seen:
                cleaned.append(i)
        return cleaned

    try:
        ranked = json.loads(out).get("ranked", [])
        ranked = _normalize(ranked, len(candidates))
        return ranked[: min(top_k, len(candidates))]
    except Exception:
        # 파싱 실패/예외 시: 원래 순서를 사용(최소한 동작 보장)
        return list(range(min(top_k, len(candidates))))


def _format_citation(meta: Dict[str, Any]) -> str:
    """
    meta로부터 통일된 citation 문자열을 만든다.

    형식:
        [source_or_url|p{page}|c{chunk_id}]

    Args:
        meta: chunk meta dict (source/url/page/chunk_id 등을 포함 가능)

    Returns:
        citation 문자열(예: "[paper.pdf|p3|c12]")

    Notes:
        - source가 없으면 url, 그것도 없으면 unknown 사용
        - page/cid가 None 또는 ""이면 생략
    """
    # - 답변과 evidence 출력에서 통일된 citation 문자열을 만듭니다.
    # - meta의 source/url, page, chunk_id를 조합해 추적 가능하게 합니다.
    # - 예: [file.pdf|p3|c12], [https://...|p0|c5]
    src = meta.get("source") or meta.get("url") or "unknown"
    page = meta.get("page")
    cid = meta.get("chunk_id")

    parts = [str(src)]
    if page is not None and page != "":
        parts.append(f"p{page}")
    if cid is not None and cid != "":
        parts.append(f"c{cid}")
    return "[" + "|".join(parts) + "]"


# -----------------------
# 3-4) Retrieval: rewrite -> fetch_k -> MMR -> rerank
# -----------------------
def retrieve(
    client: OpenAI,
    vindex: VectorIndex,
    query: str,
    top_k: int = 4,
    fetch_k: Optional[int] = None,
    use_rewrite: bool = True,
    use_mmr: bool = True,
    mmr_lambda: float = 0.5,
    use_rerank: bool = True,
) -> Tuple[str, List[Tuple[Dict[str, Any], float]]]:
    """
    실습 3단계 Retrieval 파이프라인(메인 엔진).

    Pipeline:
        1) (선택) Query rewrite: 사용자 질문 -> 검색용 짧은 질의(search_query)
        2) FAISS 후보 검색: search_query로 fetch_k개 후보 확보
        3) (선택) MMR 선택: 후보에서 top_k개를 '중복 감소' 기준으로 선택
        4) (선택) LLM rerank: top_k 후보를 '직접 답 근거' 기준으로 재정렬

    Args:
        client: OpenAI 클라이언트
        vindex: VectorIndex(FAISS + chunks + vectors)
        query: 사용자 질문
        top_k: 최종 반환할 근거 수
        fetch_k: FAISS에서 먼저 뽑을 후보 수(클수록 recall↑, 비용/시간↑)
        use_rewrite: 검색용 질의 리라이트 사용 여부
        use_mmr: MMR 적용 여부
        mmr_lambda: MMR 관련성/다양성 균형 파라미터
        use_rerank: LLM rerank 적용 여부

    Returns:
        (search_query, hits)
        - search_query: 실제 검색에 사용된 질의(리라이트 결과)
        - hits: [(chunk_dict, score), ...] (길이 <= top_k)

    Notes:
        - score는 cosine similarity(정규화 내적)로 해석 가능
        - fetch_k가 전체 chunk 수보다 클 수 있으므로 실제 사용에서는 min 처리도 고려 가능
    """
    # - 3단계 Retrieval 파이프라인을 한 함수로 묶은 “메인 엔진”입니다.
    # - rewrite로 검색 질의를 만든 뒤, FAISS에서 fetch_k개 후보를 확보합니다.
    # - MMR로 top_k를 뽑고, rerank로 “직접 답 근거”가 앞에 오도록 재정렬합니다.
    search_query = rewrite_query(client, query) if use_rewrite else query
    fk = fetch_k if fetch_k is not None else max(top_k * 4, 20)

    # search_query 임베딩(정규화 포함) -> shape (1, d)
    qv = embed_texts(client, [search_query])  # [1, d] normalized

    # FAISS에서 fk개 후보 검색
    scores, ids = vindex.index.search(qv, fk)

    # -1 제거 후 후보 인덱스 리스트화
    cand_ids = [int(i) for i in ids[0] if i != -1]

    # 1) pick via MMR (or plain top-k)
    if use_mmr and len(cand_ids) > top_k:
        picked_ids = _mmr_select(
            qvec=qv[0],
            cand_ids=cand_ids,
            vectors=vindex.vectors,
            k=top_k,
            lambda_mult=mmr_lambda,
        )
    else:
        # MMR을 끄거나 후보가 적으면 단순 상위 top_k 사용
        picked_ids = cand_ids[:top_k]

    # picked: (chunk_dict, score) 리스트
    # score는 qv[0] · vectors[i]로 계산(정규화 내적=cosine)
    picked = [(vindex.chunks[i], float(np.dot(qv[0], vindex.vectors[i]))) for i in picked_ids]

    # 2) rerank (by LLM)
    if use_rerank and len(picked) > 1:
        cand_chunks = [c for (c, _) in picked]
        order = rerank_llm(client, query, cand_chunks, top_k=len(cand_chunks))
        picked = [picked[i] for i in order]

    return search_query, picked


def answer_with_rag(
    client: OpenAI,
    query: str,
    retrieved: List[Tuple[Dict[str, Any], float]]
) -> str:
    """
    retrieval 결과를 Evidence로 구성해 근거 기반 답변을 생성한다.

    목표:
        - 제공된 evidence 외 지식 사용 금지
        - 근거 부족 시: 무엇이 부족한지 + clarifying question 1개만 요청
        - 최종 답변에 citation([source|p?|c?])을 반드시 포함하도록 강제

    Args:
        client: OpenAI 클라이언트
        query: 사용자 질문
        retrieved: [(chunk_dict, score), ...]

    Returns:
        LLM이 생성한 답변 문자열(요약 + 최종 답변)

    Notes:
        - evidence 블록에는 score와 함께 citation을 포함해 디버깅/검증을 돕는다.
        - citation 형식은 _format_citation(meta)로 통일한다.
    """
    # - retrieval 결과를 Evidence 블록으로 구성해 “근거 기반 답변”을 강제합니다.
    # - 근거가 부족하면 부족한 점을 말하고 clarifying question 1개만 하도록 합니다.
    # - 최종 답변에 [source|p?|c?] 인용을 반드시 포함하도록 프롬프트로 고정합니다.
    blocks = []
    for i, (ch, score) in enumerate(retrieved, start=1):
        cite = _format_citation(ch.get("meta", {}))
        blocks.append(f"[{i}] {cite} (score={score:.3f})\n{ch.get('text','')}")
    evidence = "\n\n".join(blocks)

    prompt = f"""
You are a RAG assistant. Use ONLY the provided evidence.
If evidence is insufficient, say what is missing and ask one clarifying question.
You MUST cite sources in the final answer using the citation format like [source|p3|c12].

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
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=600,
    )
    return r.choices[0].message.content.strip()
