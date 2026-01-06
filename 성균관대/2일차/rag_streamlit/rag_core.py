from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple

import os
import numpy as np
import faiss
from openai import OpenAI


# =========================================
# 모델 설정
# =========================================
# 임베딩 모델: 텍스트 -> 벡터 변환에 사용
EMBED_MODEL = "text-embedding-3-small"

# 채팅 모델: 최종 답변 생성(RAG Answer)에 사용
# (ChatCompletions API 기반 구버전 스타일)
CHAT_MODEL = "gpt-4-0613"


def get_client() -> OpenAI:
    """
    환경변수 OPENAI_API_KEY로 OpenAI 클라이언트를 생성한다.

    Returns:
        OpenAI: 인증된 OpenAI 클라이언트

    Raises:
        RuntimeError: OPENAI_API_KEY가 설정되어 있지 않으면 예외 발생

    Notes:
        - Streamlit에서는 secrets 또는 세션 입력값을 환경변수로 주입할 수도 있다.
    """
    key = os.getenv("OPENAI_API_KEY") or ""
    if not key:
        # streamlit secrets 사용 시 app.py에서 env로 주입해도 됨
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=key)


def embed_texts(client: OpenAI, texts: List[str]) -> np.ndarray:
    """
    여러 텍스트를 임베딩 벡터로 변환하고, 코사인 유사도 검색을 위해 L2 정규화까지 수행한다.

    Args:
        client: OpenAI 클라이언트
        texts: 임베딩할 텍스트 리스트

    Returns:
        np.ndarray: (N, d) 형태의 float32 임베딩 행렬 (L2 정규화 완료)

    Notes:
        - faiss.IndexFlatIP는 inner product(내적)를 사용한다.
        - 벡터를 L2 정규화하면, 내적 = 코사인 유사도와 동일해진다.
        - faiss.normalize_L2는 행(row) 단위로 정규화한다.
    """
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)

    # OpenAI 응답에서 embedding 벡터만 추출해 numpy 배열로 변환
    vecs = np.array([d.embedding for d in resp.data], dtype=np.float32)

    # cosine 유사도 검색을 위해 L2 normalize (각 행 벡터의 길이를 1로 맞춤)
    faiss.normalize_L2(vecs)
    return vecs


@dataclass
class VectorIndex:
    """
    FAISS 인덱스와 원문 chunks를 함께 들고 있는 간단한 컨테이너.

    index:
        FAISS 인덱스 객체 (여기서는 IndexFlatIP 사용)
    chunks:
        인덱스에 들어간 각 벡터에 대응하는 텍스트 청크 리스트
        - index의 i번째 벡터 <-> chunks[i] 텍스트
    """
    index: faiss.Index
    chunks: List[str]


def build_faiss_index(client: OpenAI, chunks: List[str]) -> VectorIndex:
    """
    chunks를 임베딩하여 FAISS 인덱스를 만들고 반환한다.

    Args:
        client: OpenAI 클라이언트
        chunks: 문서를 분할한 텍스트 조각 리스트

    Returns:
        VectorIndex: (faiss index + chunks) 묶음

    Steps:
        1) chunks 임베딩 생성 및 정규화
        2) 벡터 차원(dimension) 확인
        3) IndexFlatIP(내적 기반) 인덱스 생성
        4) 벡터를 인덱스에 추가(add)
    """
    vecs = embed_texts(client, chunks)
    dim = vecs.shape[1]

    # Inner Product 기반 인덱스
    # - 벡터를 normalize_L2 해두었기 때문에 IP = cosine similarity
    index = faiss.IndexFlatIP(dim)

    # 벡터 추가: add된 순서가 곧 chunk 인덱스와 대응됨
    index.add(vecs)

    return VectorIndex(index=index, chunks=chunks)


def retrieve(client: OpenAI, vindex: VectorIndex, query: str, top_k: int = 4) -> List[Tuple[str, float]]:
    """
    사용자의 query로 FAISS에서 top_k개의 관련 chunk를 검색한다.

    Args:
        client: OpenAI 클라이언트
        vindex: 미리 구축한 VectorIndex (FAISS 인덱스 + chunks)
        query: 사용자 질문(검색 질의)
        top_k: 가져올 결과 개수

    Returns:
        List[Tuple[str, float]]:
            [(chunk_text, score), ...]
            - score는 cosine similarity(정규화된 벡터 내적 값)

    Notes:
        - qv는 (1, d) 형태로 임베딩된다.
        - index.search는 (scores, ids)를 반환한다.
          scores.shape = (1, top_k), ids.shape = (1, top_k)
    """
    # query를 임베딩 (결과 shape: (1, d))
    qv = embed_texts(client, [query])

    # FAISS 검색: 상위 top_k의 점수와 인덱스(=chunk id)
    scores, ids = vindex.index.search(qv, top_k)

    results: List[Tuple[str, float]] = []
    for i, s in zip(ids[0], scores[0]):
        # FAISS에서 결과가 없을 경우 -1이 올 수 있어 방어
        if i == -1:
            continue
        results.append((vindex.chunks[int(i)], float(s)))

    return results


def answer_with_rag(client: OpenAI, query: str, retrieved: List[Tuple[str, float]]) -> str:
    """
    검색된 근거(retrieved)를 프롬프트에 넣어 LLM이 근거 기반으로 답변하도록 한다.

    Args:
        client: OpenAI 클라이언트
        query: 사용자 질문
        retrieved: retrieve 결과 [(chunk_text, score), ...]

    Returns:
        str: LLM이 생성한 최종 답변 문자열

    Prompt Policy:
        - "제공된 evidence만 사용"하도록 강제
        - 근거가 부족하면 무엇이 부족한지 말하고, 명확화 질문 1개 요청
        - 출력 형식: (1) Evidence summary (2) Final answer
    """
    # evidence 구성: 점수는 UI에서 보여주고, 답변 프롬프트에는 텍스트만 넣는 형태
    evidence = "\n\n".join([f"[{i+1}] {txt}" for i, (txt, _) in enumerate(retrieved)])

    prompt = f"""
You are a RAG assistant. Use ONLY the provided evidence.
If evidence is insufficient, say what is missing and ask one clarifying question.

Question:
{query}

Evidence:
{evidence}

Write:
1) Evidence summary (3-6 bullets)
2) Final answer (concise)
"""

    # ChatCompletions API 호출로 답변 생성
    r = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,  # 약간의 자연스러운 문장 생성 허용
        max_tokens=400,   # 요약+최종답변 정도 길이
    )
    return r.choices[0].message.content.strip()
