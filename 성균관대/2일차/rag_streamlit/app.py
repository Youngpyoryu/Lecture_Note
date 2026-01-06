import streamlit as st
from openai import OpenAI

# 사용자 정의 모듈:
# - loaders: PDF/웹/노트에서 텍스트를 가져오고, 텍스트를 chunk로 쪼개는 유틸
# - rag_core: FAISS 인덱스 생성, 검색(retrieve), 근거 기반 답변(answer_with_rag) 로직
from loaders import load_pdf_text, load_web_text, chunk_text
from rag_core import build_faiss_index, retrieve, answer_with_rag

# =========================================
# 0) Streamlit 기본 설정
# =========================================
# layout="wide": 좌우 컬럼을 넓게 쓰는 UI(근거/답변을 같이 보여주기 좋음)
st.set_page_config(page_title="RAG Chatbot", layout="wide")
st.title("RAG Chatbot (PDF / Web / Notes)")

# =========================================
# 1) API Key 입력 UI (Streamlit 실행 후 사용자가 입력)
# =========================================
# - type="password": 화면에 키가 마스킹되어 표시됨
# - st.session_state: 새로고침/재실행 전까지 세션에만 저장(디스크 저장 아님)
with st.sidebar:
    st.header("0) OpenAI API Key")
    api_key = st.text_input(
        "OPENAI_API_KEY",
        type="password",
        placeholder="sk-...",
        help="세션에만 저장됩니다. 새로고침/재실행 시 다시 입력 필요."
    )
    # 키가 입력되면 세션 상태에 저장
    if api_key:
        st.session_state["OPENAI_API_KEY"] = api_key


def get_client_from_session() -> OpenAI:
    """
    세션에 저장된 OPENAI_API_KEY로 OpenAI 클라이언트를 생성한다.

    - 교육/실습에서 흔히 하는 패턴:
      1) 사용자에게 키 입력받기
      2) 세션 상태에 저장
      3) 필요 시마다 client 생성

    Raises:
        RuntimeError: 키가 없거나, 형식이 sk-로 시작하지 않으면 예외 발생
    """
    key = st.session_state.get("OPENAI_API_KEY", "").strip()
    if not key.startswith("sk-"):
        raise RuntimeError("API Key가 필요합니다. 사이드바에 sk-로 시작하는 키를 입력하세요.")
    return OpenAI(api_key=key)


# =========================================
# 2) (사이드바) 문서 입력 UI
# =========================================
with st.sidebar:
    st.header("1) 문서 입력")

    # 문서 소스 선택: PDF/웹/노트 중 하나
    mode = st.radio("소스 선택", ["PDF 업로드", "웹 URL", "노트 입력"], index=0)

    # source_text: 최종적으로 retrieval에 사용할 원본 텍스트(하나의 문자열)
    source_text = ""

    if mode == "PDF 업로드":
        # PDF 업로드 위젯
        pdf = st.file_uploader("PDF 파일", type=["pdf"])
        if pdf is not None:
            # 업로드된 PDF에서 텍스트 추출 (loaders.load_pdf_text 내부 구현에 의존)
            source_text = load_pdf_text(pdf)

    elif mode == "웹 URL":
        # URL 입력 위젯
        url = st.text_input("URL")
        if url:
            # 웹 페이지에서 텍스트 추출 (크롤링/파싱은 loaders.load_web_text에 위임)
            source_text = load_web_text(url)

    else:
        # 노트/메모 텍스트 입력
        source_text = st.text_area("노트/메모 텍스트", height=220)

    # UI 구분선
    st.divider()

    # =========================================
    # 3) (사이드바) 청킹/인덱싱 UI
    # =========================================
    st.header("2) 청킹/인덱싱")

    # chunk_size: 한 chunk의 대략적인 문자 길이(또는 토큰이 아니라 문자 기반일 가능성 높음)
    chunk_size = st.slider("chunk_size", 300, 1500, 800, 50)

    # overlap: chunk를 만들 때 겹치는 길이(문맥 단절 방지 목적)
    overlap = st.slider("overlap", 0, 400, 120, 20)

    # 인덱스 생성 버튼(눌렀을 때만 인덱싱 수행)
    build_btn = st.button("인덱스 생성", type="primary")


# =========================================
# 4) 세션 상태 초기화 (한 번만)
# =========================================
# - vindex: 벡터 인덱스(FAISS)
# - chunks: 청크 목록(검색 결과 미리보기/디버깅용)
if "vindex" not in st.session_state:
    st.session_state.vindex = None
if "chunks" not in st.session_state:
    st.session_state.chunks = []

# =========================================
# 5) 인덱스 생성 로직
# =========================================
# build_btn이 눌렸을 때만 실행된다.
if build_btn:
    # 문서가 비어있으면 중단
    if not source_text.strip():
        st.error("문서 텍스트가 비어있습니다.")
    else:
        # API Key 검증 및 클라이언트 생성
        try:
            client = get_client_from_session()
        except Exception as e:
            st.error(str(e))
        else:
            # (1) 청킹: 긴 텍스트를 chunk_size / overlap 기준으로 분할
            # chunk_text가 반환하는 타입이 str 리스트인지, dict 리스트인지는 loaders 구현에 따라 다름
            chunks = chunk_text(source_text, chunk_size=chunk_size, overlap=overlap)

            # (2) 세션에 chunks 저장 (UI에서 미리보기/검색 결과 등에 사용)
            st.session_state.chunks = chunks

            # (3) FAISS 인덱스 생성: 임베딩 -> FAISS에 add 하는 과정이 내부에 포함되어 있을 가능성이 높음
            st.session_state.vindex = build_faiss_index(client, chunks)

            # 완료 메시지
            st.success(f"인덱스 생성 완료: chunks={len(chunks)}")


# =========================================
# 6) 메인 화면 레이아웃 (좌/우 컬럼)
# =========================================
col1, col2 = st.columns([1, 1])

with col1:
    st.header("3) 질문")

    # 질문 입력 UI
    q = st.text_input("질문을 입력하세요", placeholder="예: RAG가 hallucination을 줄이는 원리는?")

    # top_k: retrieval에서 뽑을 chunk 개수
    top_k = st.slider("top_k", 1, 8, 4, 1)

    # 검색+응답 버튼
    ask = st.button("검색+응답")

with col2:
    st.header("Chunk 미리보기")

    # chunks가 있으면 첫 chunk 일부를 화면에 보여준다(디버깅/학습용)
    if st.session_state.chunks:
        st.write(f"총 {len(st.session_state.chunks)} chunks")

        #  주의: chunks 원소가 문자열이라고 가정하고 [:1000] 슬라이싱
        # 만약 chunks가 dict 리스트라면 여기서 에러가 날 수 있음(구조에 맞게 수정 필요)
        st.code(st.session_state.chunks[0][:1000])


# =========================================
# 7) 검색 + 답변 생성 로직
# =========================================
if ask:
    # 인덱스가 없으면 먼저 생성하라고 안내
    if st.session_state.vindex is None:
        st.error("먼저 인덱스를 생성하세요.")

    # 질문이 비어있으면 중단
    elif not q.strip():
        st.error("질문을 입력하세요.")

    else:
        # API Key 검증 및 클라이언트 생성
        try:
            client = get_client_from_session()
        except Exception as e:
            st.error(str(e))
        else:
            # (1) retrieve: FAISS 인덱스에서 top_k개 chunk를 가져온다.
            # hits의 형태는 rag_core.retrieve 구현에 따라 달라질 수 있으나
            # 아래 코드는 (txt, score) 튜플 리스트라고 가정한다.
            hits = retrieve(client, st.session_state.vindex, q, top_k=top_k)

            # (2) Retrieved Evidence: 사용자가 근거를 직접 확인할 수 있도록 expander로 표시
            st.subheader("Retrieved Evidence")
            for i, (txt, score) in enumerate(hits, 1):
                with st.expander(f"[{i}] score={score:.3f}"):
                    st.write(txt)

            # (3) answer_with_rag: hits(근거)를 넣어 LLM이 근거 기반으로 답변 생성
            st.subheader("LLM Answer")
            ans = answer_with_rag(client, q, hits)
            st.write(ans)
