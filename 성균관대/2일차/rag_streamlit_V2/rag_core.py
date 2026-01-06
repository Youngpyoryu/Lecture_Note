# chunks를 “문자열”이 아니라 “dict(text/meta)”로 다룸
## VectorIndex.chunks를 List[str] → List[dict(text/meta)]로 변경
## retrieve 결과도 chunk dict + score 반환
## answer_with_rag에서 citation을 강제
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

import os
import numpy as np
import faiss
from openai import OpenAI

# =========================================
# 모델 설정
# =========================================
EMBED_MODEL = "text-embedding-3-small"  # 텍스트 -> 임베딩 벡터
CHAT_MODEL = "gpt-4-0613"              # 근거 기반 답변 생성(ChatCompletions 스타일)


def get_client() -> OpenAI:
    """
    환경변수 OPENAI_API_KEY로 OpenAI 클라이언트를 생성한다.

    Raises:
        RuntimeError: 환경변수에 키가 없으면 예외 발생
    """
    key = os.getenv("OPENAI_API_KEY") or ""
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=key)


def embed_texts(client: OpenAI, texts: List[str]) -> np.ndarray:
    """
    텍스트 리스트를 임베딩 벡터로 변환하고 L2 정규화까지 수행한다.

    Returns:
        (N, d) float32 numpy 배열. 각 row는 L2 normalize되어 있음.

    Notes:
        - FAISS IndexFlatIP는 내적(inner product) 기반.
        - 임베딩을 L2 정규화하면 내적 = 코사인 유사도와 동일해진다.
    """
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)

    # OpenAI 응답(resp.data)에서 embedding만 추출
    vecs = np.array([d.embedding for d in resp.data], dtype=np.float32)

    # 코사인 유사도 검색을 위해 벡터를 L2 정규화
    faiss.normalize_L2(vecs)
    return vecs


@dataclass
class VectorIndex:
    """
    FAISS 인덱스 + 원문 chunk 정보를 함께 들고 있는 자료구조.

    index:
        FAISS 인덱스(여기서는 IndexFlatIP)
    chunks:
        각 벡터에 대응하는 chunk dict의 리스트
        - chunks[i]가 index의 i번째 벡터에 대응
        - chunk dict 형태: {"text": "...", "meta": {...}}
    """
    index: faiss.Index
    chunks: List[Dict[str, Any]]  # each: {"text":..., "meta":...}


def build_faiss_index(client: OpenAI, chunks: List[Dict[str, Any]]) -> VectorIndex:
    """
    chunk dict 리스트로부터 임베딩을 만들고 FAISS 인덱스를 구성한다.

    Args:
        chunks: [{"text": "...", "meta": {...}}, ...]

    Returns:
        VectorIndex: FAISS 인덱스 + chunks를 묶어서 반환

    Steps:
        1) chunks에서 text만 뽑아 임베딩
        2) 임베딩 차원(dimension) 확인
        3) IndexFlatIP 생성 후 add(vecs)
    """
    # chunk dict에서 텍스트만 추출
    texts = [c["text"] for c in chunks]

    # 임베딩 + 정규화
    vecs = embed_texts(client, texts)

    # 벡터 차원
    dim = vecs.shape[1]

    # IP(내적) 인덱스: normalize_L2 했으므로 cosine similarity로 사용 가능
    index = faiss.IndexFlatIP(dim)

    # 인덱스에 벡터 추가 (추가 순서가 곧 chunk 인덱스)
    index.add(vecs)

    return VectorIndex(index=index, chunks=chunks)


def retrieve(
    client: OpenAI,
    vindex: VectorIndex,
    query: str,
    top_k: int = 4
) -> List[Tuple[Dict[str, Any], float]]:
    """
    query로 FAISS에서 top_k개 chunk를 검색한다.

    Args:
        vindex: VectorIndex(FAISS 인덱스 + chunk dict 리스트)
        query: 사용자 질문(검색 질의)
        top_k: 검색 상위 결과 개수

    Returns:
        [(chunk_dict, score), ...]
        - chunk_dict: {"text": "...", "meta": {...}}
        - score: 코사인 유사도(정규화된 벡터 내적 값)

    Notes:
        - index.search는 (scores, ids)를 반환
        - ids가 -1이면 결과가 없음을 의미할 수 있어 건너뛴다.
    """
    # 쿼리를 임베딩(형태: (1, d))
    qv = embed_texts(client, [query])

    # FAISS 검색
    scores, ids = vindex.index.search(qv, top_k)

    results: List[Tuple[Dict[str, Any], float]] = []
    for i, s in zip(ids[0], scores[0]):
        if i == -1:
            continue
        results.append((vindex.chunks[int(i)], float(s)))

    return results


def _format_citation(meta: Dict[str, Any]) -> str:
    """
    meta 정보로부터 citation 문자열을 만든다.

    형식:
        [source|p{page}|c{chunk_id}]
        - source가 없으면 url, 그것도 없으면 unknown
        - page/chunk_id가 None이 아니면 포함

    Args:
        meta: {"source":..., "url":..., "page":..., "chunk_id":...} 등을 포함 가능

    Returns:
        str: 예) "[paper.pdf|p3|c12]"
    """
    src = meta.get("source") or meta.get("url") or "unknown"
    page = meta.get("page")
    cid = meta.get("chunk_id")

    parts = [str(src)]
    if page is not None:
        parts.append(f"p{page}")
    if cid is not None:
        parts.append(f"c{cid}")
    return "[" + "|".join(parts) + "]"


def answer_with_rag(
    client: OpenAI,
    query: str,
    retrieved: List[Tuple[Dict[str, Any], float]]
) -> str:
    """
    검색된 evidence(근거)만으로 답하도록 LLM에 지시하여 답변을 생성한다.

    Args:
        query: 사용자 질문
        retrieved: retrieve 결과 [(chunk_dict, score), ...]

    Returns:
        str: LLM 출력(요약 + 최종 답변)

    Prompt 정책:
        - evidence 외 정보 사용 금지
        - 근거가 부족하면 부족한 점을 말하고, 명확화 질문 1개 요청
        - 최종 답변에는 반드시 citation([source|p?|c?]) 포함하도록 강제
    """
    # LLM에 넣을 evidence 블록 구성: 각 chunk에 citation + score + 본문 포함
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

    # ChatCompletions 호출
    r = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,  # 약간의 자연스러움 허용(단, 근거 제약은 프롬프트로 강제)
        max_tokens=500,
    )
    return r.choices[0].message.content.strip()