# chroma_core.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional
import os
import json

import numpy as np
import chromadb
from chromadb.config import Settings
from openai import OpenAI

# -----------------------
# 모델 설정
# -----------------------
# - 임베딩 모델: text -> vector 변환(검색의 핵심)입니다.
# - 채팅 모델: rewrite/rerank/최종 답변 생성에 사용합니다.
# - 이번 파일은 “ChromaDB로 저장/검색 + (Rewrite/MMR/Rerank 유지)”가 목표입니다.
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4-0613"


def get_client() -> OpenAI:
    # - 환경변수 OPENAI_API_KEY로 OpenAI 클라이언트를 생성합니다.
    # - 키가 없으면 즉시 예외를 내어 실습에서 원인 파악이 쉽습니다.
    # - 임베딩/리라이트/리랭크/답변 생성이 모두 같은 client를 공유합니다.
    key = os.getenv("OPENAI_API_KEY") or ""
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=key)


def embed_texts(client: OpenAI, texts: List[str]) -> np.ndarray:
    # - 텍스트 리스트를 임베딩 API로 벡터화합니다.
    # - 코사인 유사도처럼 쓰기 위해 L2 정규화를 수행합니다.
    # - 반환 shape=[N,d], dtype=float32로 유지해 연산 일관성을 보장합니다.
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    vecs = np.array([d.embedding for d in resp.data], dtype=np.float32)
    vecs /= (np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-12)
    return vecs


@dataclass
class ChromaStore:
    # - Chroma collection을 감싸는 최소 래퍼입니다.
    # - persist_path는 로컬 디스크에 DB를 저장하는 경로입니다.
    # - 컬렉션 단위로 upsert/query를 수행해 “DB처럼” 다룹니다.
    collection: Any
    persist_path: str
    name: str


def get_store(persist_path: str = "./chroma_db", name: str = "rag_chunks") -> ChromaStore:
    # - PersistentClient로 로컬에 저장되는 Chroma를 사용합니다.
    # - allow_reset은 실습에서 reset/재구성 같은 작업이 필요할 때 유용합니다.
    # - get_or_create_collection으로 컬렉션을 재사용(이미 있으면 로드)합니다.
    client = chromadb.PersistentClient(
        path=persist_path,
        settings=Settings(allow_reset=True),
    )
    col = client.get_or_create_collection(name=name)
    return ChromaStore(collection=col, persist_path=persist_path, name=name)


def _make_ids(chunks: List[Dict[str, Any]]) -> List[str]:
    # - Chroma는 각 레코드에 고유 id가 필요합니다.
    # - source/url + page + chunk_id 조합으로 재현 가능한 id를 만듭니다.
    # - 같은 문서를 다시 넣을 때도 id가 같으면 덮어쓰기(upsert)로 관리됩니다.
    ids: List[str] = []
    for c in chunks:
        meta = c.get("meta", {})
        src = meta.get("source") or meta.get("url") or "unknown"
        page = meta.get("page", "")
        cid = meta.get("chunk_id", "")
        ids.append(f"{src}|p{page}|c{cid}")
    return ids


def upsert_chunks(client: OpenAI, store: ChromaStore, chunks: List[Dict[str, Any]]) -> None:
    # - chunks(text/meta)를 Chroma 컬렉션에 저장합니다(영속화).
    # - embeddings는 우리가 직접 생성해 “모델/정규화 일관성”을 보장합니다.
    # - upsert가 없거나 환경이 다르면 delete+add로 fallback해 실습 안정성을 높입니다.
    ids = _make_ids(chunks)
    documents = [c["text"] for c in chunks]
    metadatas = [c.get("meta", {}) for c in chunks]
    embeddings = embed_texts(client, documents).tolist()

    col = store.collection
    if hasattr(col, "upsert"):
        col.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
        return

    try:
        if hasattr(col, "delete"):
            col.delete(ids=ids)
    except Exception:
        pass
    col.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)


# -----------------------
# 4-1) Query rewrite
# -----------------------
def rewrite_query(client: OpenAI, query: str) -> str:
    # - 사용자 질문을 “검색에 유리한 짧은 질의”로 재작성합니다.
    # - 핵심 엔티티/제약/기술 용어는 유지하고 군더더기는 제거합니다.
    # - 답을 생성하지 말고 한 줄만 출력하도록 규칙을 고정합니다.
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
    out = (r.choices[0].message.content or "").strip()
    return out if out else query


# -----------------------
# 4-2) MMR selection (within candidates)
# -----------------------
def _mmr_select_from_candidates(
    qvec: np.ndarray,          # [d] normalized
    cand_vecs: np.ndarray,     # [M, d] normalized
    k: int,
    lambda_mult: float = 0.5,
) -> List[int]:
    # - MMR은 후보 내에서 관련성(질의 유사도)과 다양성(후보 간 유사도)을 함께 봅니다.
    # - 후보 벡터만 있으면 동작하므로, Chroma에서도 쉽게 적용할 수 있습니다.
    # - 반환은 후보 인덱스(0..M-1) 목록이며, 이를 후보 리스트에 적용합니다.
    M = int(cand_vecs.shape[0])
    if M == 0:
        return []
    k = min(int(k), M)

    rel = (cand_vecs @ qvec).astype(np.float32)  # [M]
    selected: List[int] = []
    remaining = list(range(M))

    while remaining and len(selected) < k:
        best_i = None
        best_val = -1e9

        for i in remaining:
            r = float(rel[i])
            if not selected:
                div = 0.0
            else:
                div = float(np.max(cand_vecs[i] @ cand_vecs[selected].T))
            mmr = lambda_mult * r - (1.0 - lambda_mult) * div
            if mmr > best_val:
                best_val = mmr
                best_i = i

        selected.append(int(best_i))
        remaining.remove(int(best_i))

    return selected


# -----------------------
# 4-3) LLM rerank
# -----------------------
def rerank_llm(client: OpenAI, query: str, candidates: List[Dict[str, Any]], top_k: int) -> List[int]:
    # - 후보 chunk를 “질문에 직접 답하는 정도”로 재정렬합니다(순서만 반환).
    # - 출력은 JSON {"ranked":[...]}만 허용해 안정적인 파이프라인을 만듭니다.
    # - 출력이 깨져도 앱이 죽지 않게 안전한 순열로 정규화합니다.
    items = []
    for i, c in enumerate(candidates):
        meta = c.get("meta", {})
        src = meta.get("source") or meta.get("url") or "unknown"
        page = meta.get("page", "")
        cid = meta.get("chunk_id", "")
        items.append(
            {"i": i, "source": src, "page": page, "chunk_id": cid, "text": (c.get("text", "")[:1200])}
        )

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
    out = (r.choices[0].message.content or "").strip()

    def _normalize(order: List[int], n: int) -> List[int]:
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
        return ranked[: min(int(top_k), len(candidates))]
    except Exception:
        return list(range(min(int(top_k), len(candidates))))


def _format_citation(meta: Dict[str, Any]) -> str:
    # - 답변과 evidence 출력에서 통일된 citation 문자열을 만듭니다.
    # - source/url + page + chunk_id 조합으로 “근거 추적”이 가능하게 합니다.
    # - 예: [file.pdf|p3|c12], [https://...|c5]
    src = meta.get("source") or meta.get("url") or "unknown"
    page = meta.get("page")
    cid = meta.get("chunk_id")

    parts = [str(src)]
    if page not in (None, ""):
        parts.append(f"p{page}")
    if cid not in (None, ""):
        parts.append(f"c{cid}")
    return "[" + "|".join(parts) + "]"


def _first_query_list(x: Any) -> Optional[Any]:
    # - Chroma query 결과는 보통 “쿼리 수” 차원이 하나 더 있습니다: [ [ ... ] ] 형태
    # - 버전/옵션에 따라 list/ndarray가 섞일 수 있으므로 첫 축만 안전하게 꺼냅니다.
    # - 값이 없으면 None을 반환해 후속 로직에서 재임베딩 fallback을 할 수 있게 합니다.
    if x is None:
        return None
    try:
        if isinstance(x, list):
            return x[0] if len(x) > 0 else None
        if isinstance(x, np.ndarray):
            return x[0] if x.shape[0] > 0 else None
        return x
    except Exception:
        return None


def _has_any_embedding(embs0: Any) -> bool:
    # - numpy array는 truth value가 모호하므로 “길이/shape”로만 존재 여부를 판단합니다.
    # - list/ndarray 모두에서 안전하게 동작하도록 방어합니다.
    # - 비어있으면 False를 반환해 후보 문서를 다시 임베딩하는 흐름으로 갑니다.
    if embs0 is None:
        return False
    try:
        if isinstance(embs0, np.ndarray):
            return embs0.size > 0
        return len(embs0) > 0
    except Exception:
        return False


# -----------------------
# 4-4) Retrieval: rewrite -> chroma fetch_k -> MMR -> rerank
# -----------------------
def retrieve(
    client: OpenAI,
    store: ChromaStore,
    query: str,
    top_k: int = 4,
    fetch_k: Optional[int] = None,
    use_rewrite: bool = True,
    use_mmr: bool = True,
    mmr_lambda: float = 0.5,
    use_rerank: bool = True,
    where: Optional[Dict[str, Any]] = None,
) -> Tuple[str, List[Tuple[Dict[str, Any], float]]]:
    # - Chroma query로 후보를 fetch_k개 확보하고, MMR/rerank로 top_k를 정제합니다.
    # - query는 rewrite로 검색 친화형으로 만들고, 최종 반환은 (search_query, hits)입니다.
    # - hits는 [(chunk_dict, score), ...]이며 score는 cosine similarity입니다.
    search_query = rewrite_query(client, query) if use_rewrite else query

    fk = fetch_k if fetch_k is not None else max(top_k * 4, 20)
    fk = max(int(fk), int(top_k))

    qv = embed_texts(client, [search_query])[0]  # [d] normalized

    # - include는 버전에 따라 TypeError가 날 수 있어 try/except로 방어합니다.
    # - embeddings가 안 오면 후보 문서를 재임베딩해 MMR/점수 계산을 수행합니다.
    try:
        res = store.collection.query(
            query_embeddings=[qv.tolist()],
            n_results=fk,
            where=where,
            include=["documents", "metadatas", "embeddings", "distances"],
        )
    except TypeError:
        res = store.collection.query(
            query_embeddings=[qv.tolist()],
            n_results=fk,
            where=where,
        )

    docs0 = _first_query_list(res.get("documents", None))
    metas0 = _first_query_list(res.get("metadatas", None))
    embs0 = _first_query_list(res.get("embeddings", None))

    docs = docs0 if isinstance(docs0, list) else (docs0.tolist() if isinstance(docs0, np.ndarray) else [])
    metas = metas0 if isinstance(metas0, list) else (metas0.tolist() if isinstance(metas0, np.ndarray) else [])

    if not docs:
        return search_query, []

    # 후보 chunk 구성
    candidates: List[Dict[str, Any]] = []
    for d, m in zip(docs, metas if metas else [{}] * len(docs)):
        candidates.append({"text": d, "meta": m})

    # 후보 임베딩: 있으면 사용, 없으면 후보 문서를 재임베딩
    if _has_any_embedding(embs0):
        cand_vecs = np.asarray(embs0, dtype=np.float32)
        cand_vecs /= (np.linalg.norm(cand_vecs, axis=1, keepdims=True) + 1e-12)
    else:
        cand_vecs = embed_texts(client, docs)

    # 1) MMR로 top_k 선택
    if use_mmr and len(candidates) > top_k:
        pick_idx = _mmr_select_from_candidates(qvec=qv, cand_vecs=cand_vecs, k=top_k, lambda_mult=mmr_lambda)
    else:
        pick_idx = list(range(min(int(top_k), len(candidates))))

    picked: List[Tuple[Dict[str, Any], float]] = []
    for i in pick_idx:
        score = float(cand_vecs[i] @ qv)
        picked.append((candidates[i], score))

    # 2) rerank로 “직접 답 근거” 순서 재정렬
    if use_rerank and len(picked) > 1:
        cand_chunks = [c for (c, _) in picked]
        order = rerank_llm(client, query, cand_chunks, top_k=len(cand_chunks))
        picked = [picked[i] for i in order]

    return search_query, picked


def answer_with_rag(client: OpenAI, query: str, retrieved: List[Tuple[Dict[str, Any], float]]) -> str:
    # - retrieval 결과를 Evidence로 구성해 “근거 기반 답변”을 강제합니다.
    # - 근거가 부족하면 부족한 점을 말하고 clarifying question 1개만 하게 합니다.
    # - 최종 답변은 반드시 [source|p?|c?] 형태의 인용을 포함하도록 고정합니다.
    if not retrieved:
        return "Evidence가 부족합니다. 문서를 더 추가하거나 질문을 더 구체화해 주세요."

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
    return (r.choices[0].message.content or "").strip()
