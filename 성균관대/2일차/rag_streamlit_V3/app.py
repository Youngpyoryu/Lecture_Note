# app.py
from __future__ import annotations

import os
from typing import List, Dict, Any, Tuple

import streamlit as st

# loaders 모듈:
# - Document: "문서 단위" 데이터 구조(페이지/소스 등의 메타 포함)
# - load_pdf_documents: PDF 바이트 -> Document 리스트(페이지별)
# - load_web_document: URL -> Document 1개
# - load_notes_document: 노트 텍스트 -> Document 1개
# - make_chunks: Document 리스트 -> chunk(dict{text/meta}) 리스트
from loaders import (
    Document,
    load_pdf_documents,
    load_web_document,
    load_notes_document,
    make_chunks,
)

# rag_core 모듈:
# - get_client: 환경변수 OPENAI_API_KEY 기반 OpenAI 클라이언트 생성
# - build_faiss_index: chunk 임베딩 -> FAISS 인덱스 구축
# - retrieve: 3단계 retrieve() (search_query, hits 반환: rewrite/MMR/rerank 포함)
# - answer_with_rag: evidence(근거) 기반으로 최종 답변 생성(인용 강제 가능)
from rag_core import (
    get_client,
    build_faiss_index,
    retrieve,            # 3단계 retrieve() 사용 (search_query, hits 반환)
    answer_with_rag,
)


# -----------------------
# UI helpers
# -----------------------
def _ensure_client_from_ui_key() -> None:
    """
    사이드바에서 입력받은 API Key를 환경변수(OPENAI_API_KEY)에 동기화한다.

    왜 필요한가:
    - rag_core.get_client()가 os.environ["OPENAI_API_KEY"]를 읽는 구조라면
      Streamlit의 session_state에만 키가 있으면 get_client가 키를 못 읽는다.
    - 따라서 UI 입력값 -> env 반영을 해줘야 한다.

    동작:
    - session_state["OPENAI_API_KEY"]가 있으면 os.environ에 주입
    - 키가 없으면 아무 것도 하지 않음(이후 build/ask에서 에러로 드러나게 함)
    """
    # - 사이드바에서 받은 API Key를 환경변수에 반영합니다.
    # - rag_core.get_client()가 env에서 키를 읽기 때문에 동기화가 필요합니다.
    # - 키 미설정이면 build/ask에서 에러가 나도록 해 원인 파악을 쉽게 합니다.
    key = st.session_state.get("OPENAI_API_KEY", "").strip()
    if key:
        os.environ["OPENAI_API_KEY"] = key


def _index_identity_box(info: Dict[str, Any] | None) -> None:
    """
    중앙 안내 박스에 현재 인덱스의 정체성(소스/파라미터)을 표시한다.

    표시 목적:
    - 어떤 문서로 인덱스를 만들었는지(source_line)
    - 몇 페이지/몇 청크인지(pages/chunks)
    - 청킹 설정이 무엇이었는지(chunk_size/overlap)
    => 실험 재현성 및 사용자 혼동 방지

    Args:
        info: st.session_state.index_info (없으면 None)
    """
    # - 현재 인덱스의 정체성(문서/파라미터)을 중앙 박스에 표시합니다.
    # - pages/chunks/chunk_size/overlap을 보여 재현성을 확보합니다.
    # - 인덱스가 없으면 “없음” 상태를 안내해 사용자 흐름을 명확히 합니다.
    if not info:
        st.info("현재 인덱스: (없음)\n\n인덱스를 먼저 생성하세요.")
        return

    src_line = info.get("source_line", "unknown")
    pages = info.get("pages", "?")
    chunks = info.get("chunks", "?")
    chunk_size = info.get("chunk_size", "?")
    overlap = info.get("overlap", "?")

    st.info(
        f"현재 인덱스: {src_line}\n\n"
        f"pages={pages}|chunks={chunks}|chunk_size={chunk_size}|overlap={overlap}"
    )


def _format_hit_title(i: int, meta: Dict[str, Any], score: float) -> str:
    """
    Evidence expander의 제목을 통일된 형태로 만든다.

    형식:
        "[i] <source_or_url> p<page> c<chunk_id> | score=<score>"

    Args:
        i: 1부터 시작하는 표시용 순번
        meta: chunk의 메타데이터(dict). source/url/page/chunk_id 등을 포함 가능
        score: 유사도 점수(cosine similarity)

    Returns:
        expander 제목 문자열
    """
    # - Evidence expander 제목을 [i] source p? c? | score=? 로 통일합니다.
    # - PDF는 source/page, 웹은 url, 노트는 source=notes로 추적 가능합니다.
    # - 2단계 UI의 “검증 가능한 근거” 느낌을 그대로 유지합니다.
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
    meta 정보를 화면에 '간단한 JSON 형태'로 보여주기 위한 문자열을 생성한다.

    목적:
    - 미리보기/근거 확인 시 source/url/page/chunk_id가 한눈에 보이도록
    - 실제 JSON 파서가 아니라 "보기 좋은" 형태로 최소 키만 출력

    Args:
        meta: chunk 메타데이터 dict

    Returns:
        pseudo-json 문자열
    """
    # - Chunk 미리보기에서 meta를 JSON처럼 보여주기 위한 문자열입니다.
    # - 스크린샷처럼 source/page/chunk_id가 보이도록 최소 키만 정리합니다.
    # - url 기반일 때도 동일하게 표시해 디버깅이 쉽습니다.
    keys = ["source", "url", "page", "chunk_id"]
    lines = ["{"]  # pseudo-json
    for k in keys:
        if k in meta and meta.get(k) not in (None, ""):
            lines.append(f'  "{k}" : "{meta.get(k)}"')
    if len(lines) == 1:
        lines.append('  "info" : "no meta"')
    lines.append("}")
    return "\n".join(lines)


# -----------------------
# Streamlit App (2단계 UI 형태 유지 + 3단계 옵션 추가)
# -----------------------
# UI 설계 요약:
# - 사이드바:
#   0) Key
#   1) 문서 입력
#   2) 청킹/인덱싱
#   3) Retrieval 고급 옵션(rewrite/MMR/rerank 등)
# - 본문:
#   상단: 인덱스 정체성 박스
#   좌측: 질문/검색
#   우측: chunk 미리보기
#   하단: Retrieved Evidence + Answer
st.set_page_config(page_title="RAG Chatbot (PDF / Web / Notes)", layout="wide")
st.title("RAG Chatbot (PDF / Web / Notes)")


# =========================================
# 세션 상태 초기화
# =========================================
# Streamlit은 상호작용마다 스크립트를 다시 실행하므로
# session_state를 사용해 "상태(인덱스/청크/결과)"를 유지한다.
if "OPENAI_API_KEY" not in st.session_state:
    # 기존 환경변수에 키가 있으면 초기값으로 넣어두되, UI에서 변경 가능
    st.session_state.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if "client" not in st.session_state:
    st.session_state.client = None
if "vindex" not in st.session_state:
    st.session_state.vindex = None
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "index_info" not in st.session_state:
    st.session_state.index_info = None

# 버튼 클릭 후 결과 화면 유지용(검색용 rewrite 쿼리 + 검색 hits)
if "last_search_query" not in st.session_state:
    st.session_state.last_search_query = ""
if "last_hits" not in st.session_state:
    st.session_state.last_hits = []  # List[Tuple[chunk_dict, score]]


# -----------------------
# Sidebar: 2단계와 동일한 형태 + 3단계 옵션 섹션 추가
# -----------------------
with st.sidebar:
    # 0) API Key
    st.header("0) OpenAI API Key")
    st.text_input("OPENAI_API_KEY", key="OPENAI_API_KEY", type="password")
    _ensure_client_from_ui_key()

    st.divider()

    # 1) 문서 입력
    st.header("1) 문서 입력")
    source_kind = st.radio("소스 선택", ["PDF 업로드", "웹 URL", "노트 입력"], index=0)

    pdf_file = None
    url = ""
    notes = ""

    if source_kind == "PDF 업로드":
        pdf_file = st.file_uploader("PDF 파일", type=["pdf"])
    elif source_kind == "웹 URL":
        url = st.text_input("웹 URL", value="")
    else:
        notes = st.text_area("노트 입력", height=160)

    st.divider()

    # 2) 청킹/인덱싱
    st.header("2) 청킹/인덱싱")
    chunk_size = st.slider("chunk_size", 300, 1500, 800, 50)
    overlap = st.slider("overlap", 0, 400, 120, 10)
    build_btn = st.button("인덱스 생성", use_container_width=True)

    # 3) Retrieval 고급 옵션
    # - 3단계 retrieve()에서 사용할 옵션들을 UI로 노출
    st.divider()
    st.header("3) Retrieval 고급 옵션")
    use_rewrite = st.checkbox("Query rewrite", value=True)
    fetch_k = st.slider("fetch_k(후보 수)", 8, 80, 20, 4)
    use_mmr = st.checkbox("MMR (중복 감소)", value=True)
    mmr_lambda = st.slider("MMR lambda(관련성↔다양성)", 0.0, 1.0, 0.5, 0.05)
    use_rerank = st.checkbox("LLM Re-rank", value=True)


# -----------------------
# Build Index
# -----------------------
# 인덱스 생성 흐름:
# 1) 입력 소스(PDF/URL/Notes)를 Document 리스트로 변환
# 2) make_chunks로 chunk(dict{text/meta}) 생성
# 3) build_faiss_index로 임베딩 + FAISS 인덱스 구성
# 4) index_info 저장(재현성/디버깅용)
if build_btn:
    _ensure_client_from_ui_key()

    # (0) OpenAI 클라이언트 생성
    try:
        st.session_state.client = get_client()
    except Exception as e:
        st.session_state.client = None
        st.error(f"API Key 설정이 필요합니다: {e}")

    if st.session_state.client is not None:
        docs: List[Document] = []
        src_line = "unknown"
        pages = 0

        # (1) 소스별 문서 로딩
        if source_kind == "PDF 업로드":
            if pdf_file is None:
                st.warning("PDF를 업로드하세요.")
            else:
                # pdf_file.getvalue(): 업로드 파일 바이트
                docs = load_pdf_documents(pdf_file.getvalue(), source_name=pdf_file.name)
                src_line = pdf_file.name
                pages = len(docs)  # 페이지 수(문서 리스트 길이)

        elif source_kind == "웹 URL":
            if not url.strip():
                st.warning("URL을 입력하세요.")
            else:
                try:
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

        # (2) chunk 생성 및 인덱싱
        if docs:
            chunks = make_chunks(docs, chunk_size=chunk_size, overlap=overlap)
            st.session_state.chunks = chunks

            # chunks(dict{text/meta}) 기반으로 FAISS 인덱스 생성
            st.session_state.vindex = build_faiss_index(st.session_state.client, chunks)

            # (3) 인덱스 정체성 정보 기록
            st.session_state.index_info = {
                "source_line": src_line,
                "pages": pages,
                "chunks": len(chunks),
                "chunk_size": chunk_size,
                "overlap": overlap,
            }

            # (4) 이전 검색 결과 초기화(인덱스가 바뀌면 hits가 무의미)
            st.session_state.last_search_query = ""
            st.session_state.last_hits = []

            st.success("인덱스 생성 완료")


# -----------------------
# Main layout: (좌) 질문 / (우) Chunk 미리보기  + (하단) Evidence
# -----------------------
# 좌: 질문/검색/검색용 리라이트 쿼리 표시
# 우: 청크 미리보기(슬라이더로 chunk_id 이동)
col_left, col_right = st.columns([2, 1], gap="large")

with col_left:
    st.header("3) 질문")

    # 현재 인덱스 정보 표시(없으면 안내)
    _index_identity_box(st.session_state.index_info)

    # 질문 입력(초기값으로 예시 문장을 넣어두었음)
    q = st.text_input("질문을 입력하세요", value="예: RAG가 hallucination을 줄이는 원리는?")

    # retrieval 출력 개수
    top_k = st.slider("top_k", 1, 8, 4, 1)

    # 검색+응답 버튼
    ask_btn = st.button("검색+응답")

    if ask_btn:
        if st.session_state.vindex is None:
            st.warning("먼저 인덱스를 생성하세요.")
        else:
            # 3단계 retrieve() 호출:
            # - rewrite(search_query 생성)
            # - 후보 수(fetch_k) 만큼 1차 선별
            # - MMR로 중복 감소
            # - LLM rerank로 최종 순서 재정렬
            search_query, hits = retrieve(
                st.session_state.client,
                st.session_state.vindex,
                q,
                top_k=top_k,
                fetch_k=fetch_k,
                use_rewrite=use_rewrite,
                use_mmr=use_mmr,
                mmr_lambda=mmr_lambda,
                use_rerank=use_rerank,
            )
            st.session_state.last_search_query = search_query
            st.session_state.last_hits = hits

    # 3단계에서 추가되는 핵심 UI:
    # - 실제 검색에 쓰인(search_query) 리라이트 결과를 보여줌(디버깅/설명용)
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
        # 보고 싶은 chunk 선택
        cid = st.slider("미리볼 chunk_id", 0, n - 1, 0, 1)

        ch = chunks[cid]
        meta = ch.get("meta", {})

        # 메타를 pseudo-json으로 표시(출처/페이지/chunk_id)
        st.code(_meta_block(meta), language="json")

        # chunk 본문 표시
        st.write(ch.get("text", ""))


# -----------------------
# Retrieved Evidence (스크린샷과 동일한 느낌 유지)
# -----------------------
st.subheader("Retrieved Evidence")

hits = st.session_state.last_hits
if not hits:
    # 아직 검색을 안 했거나 결과가 없으면 안내 문구
    st.info("검색 결과가 여기에 표시됩니다.")
else:
    # 검색 결과를 expander로 표시(첫 번째 근거는 기본 expanded)
    for i, (ch, score) in enumerate(hits, start=1):
        meta = ch.get("meta", {})
        title = _format_hit_title(i, meta, score)

        with st.expander(title, expanded=(i == 1)):
            st.code(_meta_block(meta), language="json")
            st.write(ch.get("text", ""))

    # 근거 표시 아래에 최종 답변 섹션
    st.subheader("Answer")

    # answer_with_rag는 evidence만 사용하도록 프롬프트로 강제하는 형태를 기대
    ans = answer_with_rag(st.session_state.client, q, hits)
    st.write(ans)