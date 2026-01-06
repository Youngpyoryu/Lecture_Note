# pages 기반 로딩 + 인덱스 정체성 표시 + chunk 선택 미리보기
## - 인덱스 생성 시 index_meta 저장:
### mode, source, chunk_size, overlap, num_chunks
### 화면에 “현재 인덱스 정보”를 표시
### chunk 미리보기에 chunk_id 선택 슬라이더 추가

import streamlit as st
from openai import OpenAI

# loaders:
# - PDF/웹/노트 입력을 "페이지 단위 리스트"로 통일해서 반환
# - chunk_pages로 페이지 리스트를 chunk 리스트(텍스트+메타)로 변환
from loaders import load_pdf_pages, load_web_pages, load_notes_pages, chunk_pages

# rag_core:
# - build_faiss_index: chunk들을 임베딩하고 FAISS 인덱스 생성
# - retrieve: 질문(query)으로 top_k 근거 chunk 검색
# - answer_with_rag: 검색된 근거를 바탕으로 LLM 답변 생성
from rag_core import build_faiss_index, retrieve, answer_with_rag


# =========================================
# 0) Streamlit 기본 설정
# =========================================
# layout="wide": 좌/우 컬럼 UI에 유리
st.set_page_config(page_title="RAG Chatbot", layout="wide")
st.title("RAG Chatbot (PDF / Web / Notes)")


# =========================================
# 1) (사이드바) API Key 입력
# =========================================
# - type="password": 키 입력 마스킹
# - st.session_state에 저장: 세션 동안만 유지(새로고침/재실행 시 초기화 가능)
with st.sidebar:
    st.header("0) OpenAI API Key")
    api_key = st.text_input(
        "OPENAI_API_KEY",
        type="password",
        placeholder="sk-...",
        help="세션에만 저장됩니다. 새로고침/재실행 시 다시 입력 필요."
    )
    if api_key:
        st.session_state["OPENAI_API_KEY"] = api_key


def get_client_from_session() -> OpenAI:
    """
    st.session_state에 저장된 OPENAI_API_KEY로 OpenAI 클라이언트를 생성한다.

    Raises:
        RuntimeError: 키가 없거나 형식이 맞지 않으면 예외 발생
    """
    key = st.session_state.get("OPENAI_API_KEY", "").strip()
    if not key.startswith("sk-"):
        raise RuntimeError("API Key가 필요합니다. 사이드바에 sk-로 시작하는 키를 입력하세요.")
    return OpenAI(api_key=key)


# =========================================
# 2) (사이드바) 문서 입력 + 청킹/인덱싱 설정
# =========================================
with st.sidebar:
    st.header("1) 문서 입력")

    # 문서 소스 선택
    mode = st.radio("소스 선택", ["PDF 업로드", "웹 URL", "노트 입력"], index=0)

    # pages: "페이지" 단위 텍스트+메타 리스트를 담는 변수
    # - loaders.load_*_pages가 반환하는 표준 포맷이라고 가정
    pages = []

    # source_label: 인덱스 메타정보에 저장할 출처 라벨(파일명/URL/notes 등)
    source_label = ""

    if mode == "PDF 업로드":
        # PDF 파일 업로드
        pdf = st.file_uploader("PDF 파일", type=["pdf"])
        if pdf is not None:
            # PDF를 페이지 단위로 로딩(텍스트 추출+페이지 번호 메타 포함을 기대)
            pages = load_pdf_pages(pdf)

            # 업로드 파일명(가능하면) 저장
            source_label = getattr(pdf, "name", "uploaded.pdf")

    elif mode == "웹 URL":
        # URL 입력
        url = st.text_input("URL")
        if url:
            # URL의 내용을 페이지(또는 섹션) 단위로 로딩
            pages = load_web_pages(url)
            source_label = url

    else:
        # 노트 입력(텍스트 영역)
        note_text = st.text_area("노트/메모 텍스트", height=220)
        if note_text.strip():
            # 노트 텍스트를 "페이지 리스트"로 감싸는 로더
            pages = load_notes_pages(note_text)
            source_label = "notes"

    st.divider()

    # 청킹/인덱싱 파라미터
    st.header("2) 청킹/인덱싱")
    chunk_size = st.slider("chunk_size", 300, 1500, 800, 50)
    overlap = st.slider("overlap", 0, 400, 120, 20)

    # 인덱스 생성 버튼
    build_btn = st.button("인덱스 생성", type="primary")


# =========================================
# 3) 세션 상태 초기화
# =========================================
# vindex:
# - FAISS 인덱스와 chunk 매핑 정보를 가진 객체(rag_core.VectorIndex 등)
# chunks:
# - chunk_pages 결과(각 chunk는 {"text":..., "meta":...} 형태를 기대)
# index_meta:
# - 현재 인덱스가 어떤 설정/소스에서 생성되었는지 표시용 정보
if "vindex" not in st.session_state:
    st.session_state.vindex = None
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "index_meta" not in st.session_state:
    st.session_state.index_meta = None


# =========================================
# 4) 인덱스 생성 로직
# =========================================
if build_btn:
    # 페이지가 비어 있으면 인덱스 생성 불가
    if not pages:
        st.error("문서가 비어있습니다. PDF/URL/노트를 입력하세요.")
    else:
        try:
            # (1) 클라이언트 생성(키 검증 포함)
            client = get_client_from_session()

            # (2) 페이지 리스트 -> chunk 리스트로 변환
            # 기대 포맷: chunks = [{"text": "...", "meta": {...}}, ...]
            chunks = chunk_pages(pages, chunk_size=chunk_size, overlap=overlap)

            # (3) 세션에 chunk 저장(미리보기/근거 표시용)
            st.session_state.chunks = chunks

            # (4) FAISS 인덱스 생성(임베딩->index.add)
            st.session_state.vindex = build_faiss_index(client, chunks)

            # (5) 현재 인덱스의 생성 조건을 메타로 저장(사용자에게 표시하기 좋음)
            st.session_state.index_meta = {
                "mode": mode,
                "source": source_label,
                "chunk_size": chunk_size,
                "overlap": overlap,
                "num_pages": len(pages),
                "num_chunks": len(chunks),
            }

            st.success(f"인덱스 생성 완료: chunks={len(chunks)}")

        except Exception as e:
            # 로딩/청킹/임베딩/FAISS 등 어디서든 예외 가능 → 사용자에게 표시
            st.error(str(e))


# =========================================
# 5) 메인 UI: 좌(질문/검색) / 우(chunk 미리보기)
# =========================================
col1, col2 = st.columns([1, 1])

with col1:
    st.header("3) 질문")

    # 인덱스가 존재하면 현재 인덱스 정보(소스/설정)를 안내
    if st.session_state.index_meta:
        st.info(
            f"현재 인덱스: {st.session_state.index_meta['mode']} | "
            f"{st.session_state.index_meta['source']} | "
            f"pages={st.session_state.index_meta['num_pages']} | "
            f"chunks={st.session_state.index_meta['num_chunks']} | "
            f"chunk_size={st.session_state.index_meta['chunk_size']} | "
            f"overlap={st.session_state.index_meta['overlap']}"
        )

    # 질문 입력
    q = st.text_input("질문을 입력하세요", placeholder="예: RAG가 hallucination을 줄이는 원리는?")

    # 검색 결과 개수(top_k)
    top_k = st.slider("top_k", 1, 8, 4, 1)

    # 검색+응답 버튼
    ask = st.button("검색+응답")


with col2:
    st.header("Chunk 미리보기")

    # 세션에 저장된 chunks를 꺼내어 특정 chunk를 선택해 확인
    chunks = st.session_state.chunks
    if chunks:
        st.write(f"총 {len(chunks)} chunks")

        # 보고 싶은 chunk_id 선택(0 ~ N-1)
        idx = st.slider("미리볼 chunk_id", 0, len(chunks) - 1, 0, 1)

        # chunk의 meta를 JSON 형태로 표시(출처/페이지/청크 번호 등 확인용)
        st.json(chunks[idx]["meta"])

        # chunk 텍스트 일부 미리보기(너무 길면 UI가 무거워지므로 1200자 제한)
        st.code(chunks[idx]["text"][:1200])


# =========================================
# 6) 검색 + 답변 생성
# =========================================
if ask:
    # 인덱스가 없으면 검색 불가
    if st.session_state.vindex is None:
        st.error("먼저 인덱스를 생성하세요.")

    # 질문이 비어있으면 검색 불가
    elif not q.strip():
        st.error("질문을 입력하세요.")

    else:
        try:
            # (1) 클라이언트 생성
            client = get_client_from_session()

            # (2) 검색: query로 top_k개의 chunk를 가져옴
            # 기대 형태: hits = [(chunk_dict, score), ...]
            # chunk_dict = {"text":..., "meta":...}
            hits = retrieve(client, st.session_state.vindex, q, top_k=top_k)

            # (3) Retrieved Evidence: 근거를 expander로 펼쳐서 확인 가능하게 표시
            st.subheader("Retrieved Evidence")
            for i, (ch, score) in enumerate(hits, 1):
                meta = ch.get("meta", {})

                # 출처/페이지/청크번호를 타이틀에 표시
                src = meta.get("source") or meta.get("url") or "unknown"
                page = meta.get("page", "")
                cid = meta.get("chunk_id", "")
                title = f"[{i}] {src} p{page} c{cid} | score={score:.3f}"

                with st.expander(title):
                    # 메타데이터를 함께 보여주면 디버깅/신뢰도 확인에 유리
                    st.json(meta)
                    st.write(ch.get("text", ""))

            # (4) 최종 답변 생성: evidence를 넣어 근거 기반 답변 생성
            st.subheader("LLM Answer")
            ans = answer_with_rag(client, q, hits)
            st.write(ans)

        except Exception as e:
            # 검색/답변 과정에서 발생하는 모든 예외를 사용자에게 표시
            st.error(str(e))
