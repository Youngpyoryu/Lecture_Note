# app.py
# 목적:
# - Streamlit UI로 문서(PDF/Web/Notes)를 받아 청킹 → ChromaDB 저장(Upsert) → 검색(Retrieval) → RAG 답변 생성까지 한 화면에서 실습/시연
# - “근거 기반 RAG”를 위해 Evidence(메타+원문 chunk) 를 UI에 노출

from __future__ import annotations

import os
from typing import List, Dict, Any, Tuple

import streamlit as st

# loaders: 문서 입력(PDF/웹/노트) → Document 리스트 → chunk 생성까지 담당
from loaders import (
    Document,
    load_pdf_documents,
    load_web_document,
    load_notes_document,
    make_chunks,
)

# chroma_core: OpenAI client 생성, Chroma store 연결/생성, upsert, retrieve, 최종 답변 생성 담당
from chroma_core import (
    get_client,
    get_store,
    upsert_chunks,
    retrieve,
    answer_with_rag,
)

# -----------------------
# UI helpers
# -----------------------
def _ensure_client_from_ui_key() -> None:
    """
    사이드바에서 입력한 OpenAI API Key를 환경변수에 반영.
    - chroma_core.get_client()는 os.environ["OPENAI_API_KEY"]를 참조하도록 설계되어 있으므로
      UI 입력값과 환경변수를 동기화해야 함.
    """
    key = st.session_state.get("OPENAI_API_KEY", "").strip()
    if key:
        os.environ["OPENAI_API_KEY"] = key


def _index_identity_box(info: Dict[str, Any] | None) -> None:
    """
    현재 인덱스(=Chroma 컬렉션)가 어떤 소스/파라미터로 만들어졌는지 표시.
    - 실습/강의에서 재현성을 강조하기 위해 pages/chunks/chunk_size/overlap/db를 노출
    """
    if not info:
        st.info("현재 인덱스: (없음)\n\n인덱스를 먼저 생성하세요.")
        return

    # 인덱스 식별 정보(출처, 문서 페이지 수, chunk 수, 청킹 파라미터, DB 경로)
    src_line = info.get("source_line", "unknown")
    pages = info.get("pages", "?")
    chunks = info.get("chunks", "?")
    chunk_size = info.get("chunk_size", "?")
    overlap = info.get("overlap", "?")
    db = info.get("db", "chroma_db/?")

    st.info(
        f"현재 인덱스: {src_line}\n\n"
        f"pages={pages}|chunks={chunks}|chunk_size={chunk_size}|overlap={overlap}\n"
        f"db={db}"
    )


def _format_hit_title(i: int, meta: Dict[str, Any], score: float) -> str:
    """
    Evidence(expander) 제목 포맷 통일:
    - [i] source(or url) p{page} c{chunk_id} | score=...
    - source/url/page/chunk_id는 검증 가능한 RAG의 최소 추적 정보
    """
    src = meta.get("source") or meta.get("url") or "unknown"
    page = meta.get("page")
    cid = meta.get("chunk_id")

    parts = [str(src)]
    if page not in (None, ""):
        parts.append(f"p{page}")
    if cid not in (None, ""):
        parts.append(f"c{cid}")

    return f"[{i}] " + " ".join(parts) + f" | score={score:.3f}"


def _meta_block(meta: Dict[str, Any]) -> str:
    """
    meta를 사람이 읽기 쉬운 JSON 형태로 출력.
    - 핵심 추적 키(source/url/page/chunk_id)만 우선 노출
    """
    keys = ["source", "url", "page", "chunk_id"]
    lines = ["{"]
    wrote = False
    for k in keys:
        v = meta.get(k)
        if v not in (None, ""):
            lines.append(f'  "{k}" : "{v}"')
            wrote = True
    if not wrote:
        lines.append('  "info" : "no meta"')
    lines.append("}")
    return "\n".join(lines)


# -----------------------
# Streamlit App
# -----------------------
# UI 구성:
# - Sidebar: Key 입력, 문서 입력(PDF/Web/Notes), 청킹/인덱싱 옵션, Retrieval 고급 옵션
# - Main(left): 인덱스 정체성 + 질문 + 검색/응답 트리거
# - Main(right): chunk 미리보기(디버깅/학습용)
# - Bottom: Retrieved Evidence + Answer
st.set_page_config(page_title="RAG Chatbot (PDF / Web / Notes)", layout="wide")
st.title("RAG Chatbot (PDF / Web / Notes)")

# -----------------------
# Session State 초기화
# -----------------------
# Streamlit은 rerun 기반이라 상태를 session_state에 저장해 화면/버튼 동작을 안정화
if "OPENAI_API_KEY" not in st.session_state:
    st.session_state.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if "client" not in st.session_state:
    st.session_state.client = None
if "store" not in st.session_state:
    st.session_state.store = None
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "index_info" not in st.session_state:
    st.session_state.index_info = None

# “검색 버튼 클릭 후 결과 유지”를 위한 상태
if "last_search_query" not in st.session_state:
    st.session_state.last_search_query = ""
if "last_hits" not in st.session_state:
    # hits: List[Tuple[chunk_dict, score]]
    st.session_state.last_hits = []

# -----------------------
# Sidebar
# -----------------------
with st.sidebar:
    # 0) API Key 입력
    st.header("0) OpenAI API Key")
    st.text_input("OPENAI_API_KEY", key="OPENAI_API_KEY", type="password")
    _ensure_client_from_ui_key()

    st.divider()

    # 1) 문서 입력
    st.header("1) 문서 입력")
    source_kind = st.radio("소스 선택", ["PDF 업로드", "웹 URL", "노트 입력"], index=0)

    # 입력값 초기화(선택된 소스만 실제로 사용)
    pdf_file = None
    url = ""
    notes = ""

    if source_kind == "PDF 업로드":
        # Streamlit file_uploader는 UploadedFile 객체를 반환
        pdf_file = st.file_uploader("PDF 파일", type=["pdf"])
    elif source_kind == "웹 URL":
        url = st.text_input("웹 URL", value="")
    else:
        notes = st.text_area("노트 입력", height=160)

    st.divider()

    # 2) 청킹/인덱싱 옵션
    st.header("2) 청킹/인덱싱")
    chunk_size = st.slider("chunk_size", 300, 1500, 800, 50)
    overlap = st.slider("overlap", 0, 400, 120, 10)

    # Chroma 저장 경로/컬렉션
    # - 강의에서 “벡터DB를 파일/컬렉션 단위로 관리한다”를 보여주기 위해 노출
    persist_path = st.text_input("Chroma persist_path", value="./chroma_db")
    collection_name = st.text_input("Chroma collection", value="rag_chunks")

    # 인덱스 생성 버튼
    build_btn = st.button("인덱스 생성", use_container_width=True)

    st.divider()

    # 3) Retrieval 고급 옵션
    # - rewrite: 질문을 검색에 유리한 형태로 재작성
    # - fetch_k: 후보를 넉넉히 뽑고(top_k보다 큼), MMR/리랭크로 정제
    # - MMR: 중복 감소(다양성 확보)
    # - rerank: LLM이 후보들을 재정렬(비용/시간 증가 가능)
    st.header("3) Retrieval 고급 옵션")
    use_rewrite = st.checkbox("Query rewrite", value=True)
    fetch_k = st.slider("fetch_k(후보 수)", 8, 80, 20, 4)
    use_mmr = st.checkbox("MMR (중복 감소)", value=True)
    mmr_lambda = st.slider("MMR lambda(관련성↔다양성)", 0.0, 1.0, 0.5, 0.05)
    use_rerank = st.checkbox("LLM Re-rank", value=True)

# -----------------------
# Build Index (Chroma upsert)
# -----------------------
# 동작:
# 1) 소스 로드(PDF/Web/Notes) → Document list
# 2) 청킹(make_chunks) → chunk dict list (text + meta)
# 3) Chroma store 연결(get_store) → upsert_chunks로 임베딩 후 저장
# 4) index_info 업데이트(재현성/디버깅 정보)
if build_btn:
    _ensure_client_from_ui_key()

    # OpenAI client 생성(키가 없으면 여기서 에러)
    try:
        st.session_state.client = get_client()
    except Exception as e:
        st.session_state.client = None
        st.error(f"API Key 설정이 필요합니다: {e}")

    if st.session_state.client is not None:
        docs: List[Document] = []
        src_line = "unknown"
        pages = 0

        # 선택한 입력 소스에 따라 문서 로딩
        if source_kind == "PDF 업로드":
            if pdf_file is None:
                st.warning("PDF를 업로드하세요.")
            else:
                # PDF는 페이지 단위 Document 리스트로 로드
                docs = load_pdf_documents(pdf_file.getvalue(), source_name=pdf_file.name)
                src_line = pdf_file.name
                pages = len(docs)

        elif source_kind == "웹 URL":
            if not url.strip():
                st.warning("URL을 입력하세요.")
            else:
                try:
                    # 웹은 단일 Document로 로드(필요하면 내부에서 길이에 따라 분할 가능)
                    docs = [load_web_document(url.strip())]
                    src_line = url.strip()
                    pages = 1
                except Exception as e:
                    st.error(f"URL 로딩 실패: {e}")

        else:  # 노트 입력
            if not notes.strip():
                st.warning("노트를 입력하세요.")
            else:
                docs = [load_notes_document(notes.strip())]
                src_line = "notes"
                pages = 1

        # 문서가 정상적으로 로드되면 청킹 후 Chroma에 저장
        if docs:
            # chunk: {"text": "...", "meta": {...}} 형태를 가정
            chunks = make_chunks(docs, chunk_size=chunk_size, overlap=overlap)
            st.session_state.chunks = chunks

            # Chroma store 생성/연결
            st.session_state.store = get_store(persist_path=persist_path, name=collection_name)

            # 임베딩 생성 후 upsert (실제 벡터DB에 저장)
            upsert_chunks(st.session_state.client, st.session_state.store, chunks)

            # 인덱스 정체성 기록(강의/재현성/디버깅)
            st.session_state.index_info = {
                "source_line": src_line,
                "pages": pages,
                "chunks": len(chunks),
                "chunk_size": chunk_size,
                "overlap": overlap,
                "db": f"{persist_path}/{collection_name}",
            }

            # 이전 검색 결과 초기화(새 인덱스이므로)
            st.session_state.last_search_query = ""
            st.session_state.last_hits = []
            st.success("인덱스 생성 완료 (Chroma에 저장됨)")

# -----------------------
# Main layout
# -----------------------
# 좌/우 컬럼: 질문/검색 + chunk 미리보기
col_left, col_right = st.columns([2, 1], gap="large")

with col_left:
    st.header("3) 질문")
    # 인덱스 존재/정체성 안내
    _index_identity_box(st.session_state.index_info)

    # 사용자 질문 입력
    q = st.text_input("질문을 입력하세요", value="예: HNSW가 벡터 검색에서 하는 역할은?")
    # 최종 반환 개수(top_k)
    top_k = st.slider("top_k", 1, 8, 4, 1)

    # 검색+응답 버튼
    ask_btn = st.button("검색+응답")

    if ask_btn:
        # 인덱스를 생성하지 않았으면 검색 불가
        if st.session_state.store is None:
            st.warning("먼저 인덱스를 생성하세요.")
        else:
            # retrieve:
            # - (옵션) rewrite → search_query 생성
            # - 후보 fetch_k 만큼 가져온 뒤
            # - (옵션) MMR 적용
            # - (옵션) LLM rerank 적용
            # - top_k로 잘라 반환
            search_query, hits = retrieve(
                st.session_state.client,
                st.session_state.store,
                q,
                top_k=top_k,
                fetch_k=fetch_k,
                use_rewrite=use_rewrite,
                use_mmr=use_mmr,
                mmr_lambda=mmr_lambda,
                use_rerank=use_rerank,
                where=None,  # 필요 시 메타 필터(예: 특정 source만) 등에 사용
            )
            st.session_state.last_search_query = search_query
            st.session_state.last_hits = hits

    # rewrite를 켠 경우, 실제 검색에 사용된 질의를 표시(디버깅/학습용)
    if st.session_state.last_search_query:
        st.caption(f"검색용 질의(rewrite): {st.session_state.last_search_query}")

with col_right:
    st.header("Chunk 미리보기")

    chunks = st.session_state.chunks
    n = len(chunks)
    st.write(f"총 {n} chunks")

    if n == 0:
        st.info("인덱스를 생성하면 chunk 미리보기가 활성화됩니다.")
    else:
        # 특정 chunk_id를 골라 meta + text를 확인
        cid = st.slider("미리볼 chunk_id", 0, n - 1, 0, 1)
        ch = chunks[cid]
        meta = ch.get("meta", {})
        st.code(_meta_block(meta), language="json")
        st.write(ch.get("text", ""))

# -----------------------
# Retrieved Evidence + Answer
# -----------------------
# - Evidence: 어떤 근거(chunk)로 답을 만들었는지 사용자에게 보여줌(검증 가능성)
# - Answer: hits를 컨텍스트로 LLM이 최종 답변 생성
st.subheader("Retrieved Evidence")

hits = st.session_state.last_hits
if not hits:
    st.info("검색 결과가 여기에 표시됩니다.")
else:
    # 검색된 chunk들을 expander로 나열 (첫 번째는 기본 open)
    for i, (ch, score) in enumerate(hits, start=1):
        meta = ch.get("meta", {})
        title = _format_hit_title(i, meta, score)
        with st.expander(title, expanded=(i == 1)):
            st.code(_meta_block(meta), language="json")
            st.write(ch.get("text", ""))

    st.subheader("Answer")
    # answer_with_rag: hits(근거) 기반으로 질문 q에 대한 답 생성
    ans = answer_with_rag(st.session_state.client, q, hits)
    st.write(ans)
