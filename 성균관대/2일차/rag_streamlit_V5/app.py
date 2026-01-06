# app.py
from __future__ import annotations

import os
import streamlit as st

from loaders import load_pdf_documents, load_web_document, load_notes_document, make_chunks
from chroma_core import (
    get_client,
    get_embed_dim,
    get_store,
    upsert_chunks,
    retrieve,
    answer_with_rag,
    EMBED_MODEL,
)

# -----------------------
# Streamlit 기본 설정
# -----------------------
# - “PDF/Web/Notes → 청킹 → 저장(Chroma) → 검색/답변” 흐름을 한 화면에서 실습합니다.
# - 2단계 UI(질문/Chunk 미리보기/Retrieved Evidence)를 유지하고 Hybrid 옵션만 추가합니다.
# - session_state로 client/store/chunks를 유지해 버튼 클릭마다 상태가 날아가지 않게 합니다.
st.set_page_config(page_title="RAG Chatbot (PDF / Web / Notes)", layout="wide")
st.title("RAG Chatbot (PDF / Web / Notes)")


def _ensure_client():
    # - OpenAI client를 세션에 1회만 생성해 재사용합니다.
    # - 키가 없으면 예외가 나므로, 실습 시작 전에 환경변수 설정이 필요합니다.
    # - 이후 임베딩/리라이트/리랭크/답변 생성에서 동일 client를 사용합니다.
    if "client" not in st.session_state:
        st.session_state.client = get_client()


def _ensure_store(persist_path: str, collection_base: str):
    # - 임베딩 차원은 컬렉션 내부에서 고정되므로, 실제 dim을 확인한 후 store를 엽니다.
    # - 컬렉션 이름에 모델/차원을 포함해 서로 다른 설정이 섞이는 것을 방지합니다.
    # - persist_path는 로컬 폴더에 DB 파일(chroma.sqlite3 등)을 유지합니다.
    _ensure_client()
    dim = get_embed_dim(st.session_state.client)
    st.session_state.embed_dim = dim
    st.session_state.store = get_store(
        persist_path=persist_path,
        collection_base=collection_base,
        embed_model=EMBED_MODEL,
        dim=dim,
    )


# -----------------------
# Sidebar: 입력/인덱싱/옵션
# -----------------------
with st.sidebar:
    st.header("0) OpenAI API Key")
    st.caption("OPENAI_API_KEY는 환경변수로 설정되어 있어야 합니다.")
    # 키는 앱에 직접 입력하지 않고(보안), OS 환경변수로만 쓰는 것을 권장합니다.
    st.code("set OPENAI_API_KEY=sk-...", language="bash")

    st.divider()
    st.header("1) 문서 입력")
    source_mode = st.radio("소스 선택", ["PDF 업로드", "웹 URL", "노트 입력"], index=0)

    pdf_file = None
    url = ""
    notes = ""

    if source_mode == "PDF 업로드":
        pdf_file = st.file_uploader("PDF 파일", type=["pdf"])
    elif source_mode == "웹 URL":
        url = st.text_input("URL", value="")
    else:
        notes = st.text_area("Notes", height=140)

    st.divider()
    st.header("2) 청킹/인덱싱")
    chunk_size = st.slider("chunk_size", 300, 1500, 800, 50)
    overlap = st.slider("overlap", 0, 400, 120, 10)

    chroma_persist_path = st.text_input("Chroma persist_path", value="./chroma_db")
    chroma_collection = st.text_input("Chroma collection", value="rag_chunks")

    build_btn = st.button("인덱스 생성", type="primary")

    st.divider()
    st.header("3) Retrieval 고급 옵션")
    use_rewrite = st.checkbox("Query rewrite", value=True)
    fetch_k = st.slider("fetch_k(후보 수)", 8, 120, 20, 4)
    use_mmr = st.checkbox("MMR (중복 감소)", value=True)
    mmr_lambda = st.slider("MMR lambda(관련성↔다양성)", 0.0, 1.0, 0.5, 0.05)
    use_rerank = st.checkbox("LLM Re-rank", value=True)

    st.divider()
    st.header("4) Hybrid Retrieval")
    use_hybrid = st.checkbox("Hybrid (Keyword + Vector)", value=False)
    alpha = st.slider("alpha (vector 비중)", 0.0, 1.0, 0.7, 0.05)
    keyword_mode = st.radio("keyword mode", ["tfidf-ish", "contains"], index=0)

# store 준비(입력 필드 기반)
if "store" not in st.session_state:
    _ensure_store(chroma_persist_path, chroma_collection)
else:
    # 사용자가 path/collection을 바꾸면 store를 다시 열어야 함
    prev = st.session_state.get("store_info", {})
    now = {"persist": chroma_persist_path, "base": chroma_collection}
    if prev != now:
        _ensure_store(chroma_persist_path, chroma_collection)

st.session_state.store_info = {"persist": chroma_persist_path, "base": chroma_collection}

# -----------------------
# Build / Upsert
# -----------------------
def _build_index():
    # - 입력(PDF/URL/Notes)을 Document로 로딩한 뒤 chunk로 변환합니다.
    # - 변환된 chunks를 Chroma에 upsert하고, 미리보기용 chunks를 session_state에 저장합니다.
    # - build_info를 만들어 “현재 인덱스 정체성(문서/파라미터)”을 화면에 표시합니다.
    docs = []
    source_label = "none"

    if source_mode == "PDF 업로드" and pdf_file is not None:
        docs = load_pdf_documents(pdf_file.getvalue(), source_name=pdf_file.name)
        source_label = pdf_file.name
    elif source_mode == "웹 URL" and url.strip():
        docs = [load_web_document(url.strip())]
        source_label = url.strip()
    elif source_mode == "노트 입력" and notes.strip():
        docs = [load_notes_document(notes)]
        source_label = "notes"

    if not docs:
        st.warning("문서가 없습니다. PDF/URL/Notes 중 하나를 입력하세요.")
        return

    chunks = make_chunks(docs, chunk_size=chunk_size, overlap=overlap)
    upsert_chunks(st.session_state.client, st.session_state.store, chunks)

    st.session_state.chunks = chunks
    st.session_state.build_info = {
        "source": source_label,
        "pages": len(docs),
        "chunks": len(chunks),
        "chunk_size": chunk_size,
        "overlap": overlap,
        "db": chroma_persist_path,
        "collection": st.session_state.store.name,
    }

if build_btn:
    _ensure_client()
    _ensure_store(chroma_persist_path, chroma_collection)
    _build_index()

# -----------------------
# Main layout: 왼쪽(질문/상태) + 오른쪽(Chunk 미리보기)
# -----------------------
colL, colR = st.columns([1.35, 1.0])

with colL:
    st.header("3) 질문")

    # 현재 인덱스 표시(2단계 형식 유지)
    info = st.session_state.get("build_info")
    if info:
        st.info(
            f"현재 인덱스: {info['source']}\n\n"
            f"pages={info['pages']} | chunks={info['chunks']} | "
            f"chunk_size={info['chunk_size']} | overlap={info['overlap']} | "
            f"db={info['db']} | collection={info['collection']}"
        )
    else:
        st.info("현재 인덱스: 없음 (사이드바에서 문서를 넣고 ‘인덱스 생성’을 누르세요)")

    q = st.text_input("질문을 입력하세요", value="예: HNSW가 벡터 검색에서 하는 역할은?")
    top_k = st.slider("top_k", 1, 8, 4, 1)
    ask_btn = st.button("검색+응답", type="primary")

    # 검색 실행
    if ask_btn:
        _ensure_client()
        store = st.session_state.store

        search_query, hits = retrieve(
            client=st.session_state.client,
            store=store,
            query=q,
            top_k=top_k,
            fetch_k=fetch_k,
            use_rewrite=use_rewrite,
            use_mmr=use_mmr,
            mmr_lambda=mmr_lambda,
            use_rerank=use_rerank,
            where=None,
            use_hybrid=use_hybrid,
            alpha=alpha,
            keyword_mode=keyword_mode,
        )

        st.session_state.last_search_query = search_query
        st.session_state.last_hits = hits

        st.caption(f"검색용 질의(rewrite): {search_query}")

with colR:
    st.header("Chunk 미리보기")

    chunks = st.session_state.get("chunks") or []
    if not chunks:
        st.caption("인덱스를 생성하면 chunk 미리보기가 활성화됩니다.")
    else:
        st.caption(f"총 {len(chunks)} chunks")
        cid = st.slider("미리볼 chunk_id", 0, max(0, len(chunks) - 1), 0, 1)
        ch = chunks[cid]
        st.json(ch.get("meta", {}))
        st.write(ch.get("text", ""))

# -----------------------
# Retrieved Evidence + Answer (아래 영역)
# -----------------------
st.subheader("Retrieved Evidence")

hits = st.session_state.get("last_hits") or []
if hits:
    for i, (ch, score) in enumerate(hits, start=1):
        meta = ch.get("meta", {})
        src = meta.get("source") or meta.get("url") or "unknown"
        page = meta.get("page", "")
        cid = meta.get("chunk_id", "")
        title = f"[{i}] {src} | p{page} | c{cid} | score={score:.3f}"
        with st.expander(title, expanded=(i == 1)):
            st.json(meta)
            st.write(ch.get("text", ""))
else:
    st.caption("아직 검색 결과가 없습니다. ‘검색+응답’을 눌러보세요.")

# 답변 생성
if hits and st.session_state.get("last_question") != q:
    st.session_state.last_question = q

if hits:
    st.subheader("Answer")
    ans = answer_with_rag(st.session_state.client, st.session_state.get("last_question", q), hits)
    st.markdown(ans)
