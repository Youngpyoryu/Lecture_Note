## app.py
### 의도: Streamlit으로 RAG 챗봇 UI를 제공하고, 전체 파이프라인(문서 입력 → 인덱스 생성 → 질문/검색 → 답변)을 한 화면에서 실행한다.
### 핵심: 사용자가 PDF/Web/Notes를 선택해 입력하고, chunk_size/overlap/top_k 및 고급 옵션(rewrite/MMR/rerank)을 조절한다.
### 상태관리: st.session_state에 API Key, chunks, 인덱스(벡터), 인덱스 메타 정보를 저장해 재사용한다.
### 출력: Retrieved Evidence(출처/페이지/chunk_id 포함)와 LLM Answer를 함께 보여줘 “근거 기반”을 눈으로 확인한다.
import streamlit as st
from openai import OpenAI

# loaders: 입력 소스별( PDF / Web / Notes ) 텍스트 로딩 + 청킹 유틸
from loaders import load_pdf_pages, load_web_pages, load_notes_pages, chunk_pages
# rag_core: 인덱스 생성(임베딩) / 검색 / RAG 답변 생성 로직
from rag_core import build_index, retrieve, answer_with_rag

# --------------------------------------------
# Streamlit 기본 UI 설정
# --------------------------------------------
st.set_page_config(page_title="RAG Chatbot (No FAISS)", layout="wide")
st.title("RAG Chatbot (No FAISS) — BruteForce Retrieval")

# --------------------------------------------
# 사이드바: 0) OpenAI API Key 입력 및 세션 저장
# --------------------------------------------
with st.sidebar:
    st.header("0) OpenAI API Key")
    # 사용자가 직접 키를 입력하도록 하고, 화면에는 마스킹
    api_key = st.text_input("OPENAI_API_KEY", type="password", placeholder="sk-...")
    if api_key:
        # 세션에 저장해 페이지 리로드/재실행에도 재사용
        st.session_state["OPENAI_API_KEY"] = api_key


def get_client_from_session() -> OpenAI:
    """
    세션에 저장된 OpenAI API Key로 OpenAI 클라이언트를 생성해 반환.
    - 키가 없거나 형식이 잘못되면 에러를 발생시켜 UI에서 안내하도록 한다.
    """
    key = st.session_state.get("OPENAI_API_KEY", "").strip()
    if not key.startswith("sk-"):
        raise RuntimeError("API Key가 필요합니다. 사이드바에 sk-로 시작하는 키를 입력하세요.")
    return OpenAI(api_key=key)


# --------------------------------------------
# 사이드바: 1) 문서 입력 (PDF / URL / Notes) + 2) 청킹/인덱싱 + 3) Retrieval 옵션
# --------------------------------------------
with st.sidebar:
    st.header("1) 문서 입력")
    # 문서 소스를 선택 (PDF/웹/노트)
    mode = st.radio("소스 선택", ["PDF 업로드", "웹 URL", "노트 입력"], index=0)

    pages = []          # 로딩된 페이지 리스트(페이지 단위 텍스트)
    source_label = ""   # 출처 표시용 라벨(파일명/URL/notes)

    if mode == "PDF 업로드":
        # PDF 파일을 업로드 받는다.
        pdf = st.file_uploader("PDF 파일", type=["pdf"])
        if pdf is not None:
            # PDF를 페이지 단위로 텍스트 추출
            pages = load_pdf_pages(pdf)
            # 메타에 기록할 source(파일명)
            source_label = getattr(pdf, "name", "uploaded.pdf")

    elif mode == "웹 URL":
        # URL 입력을 받는다.
        url = st.text_input("URL")
        if url:
            # 웹 페이지 텍스트 로딩(페이지/섹션 단위로 나뉘어 반환될 수 있음)
            pages = load_web_pages(url)
            source_label = url

    else:
        # 노트 텍스트를 직접 입력 받는다.
        note_text = st.text_area("노트/메모 텍스트", height=220)
        if note_text.strip():
            # 노트 텍스트를 "페이지" 형태로 래핑
            pages = load_notes_pages(note_text)
            source_label = "notes"

    st.divider()

    # ----------------------------------------
    # 2) 청킹/인덱싱 파라미터 설정
    # ----------------------------------------
    st.header("2) 청킹/인덱싱")
    # chunk_size: 한 chunk에 포함할 문자/토큰 근사 길이(구현에 따라 다름)
    chunk_size = st.slider("chunk_size", 300, 1500, 800, 50)
    # overlap: 인접 chunk 간 중복 영역(문맥 단절 완화 목적)
    overlap = st.slider("overlap", 0, 400, 120, 20)
    # 인덱스 생성 트리거 버튼
    build_btn = st.button("인덱스 생성", type="primary")

    st.divider()

    # ----------------------------------------
    # 3) Retrieval 고급 옵션
    # ----------------------------------------
    st.header("3) Retrieval 고급 옵션")
    # Query rewrite: 질문을 검색에 유리하도록 LLM이 재작성
    use_rewrite = st.checkbox("Query rewrite", value=True)
    # MMR: 최대 관련성 + 다양성(중복 감소) 기반 선택
    use_mmr = st.checkbox("MMR (중복 감소)", value=True)
    # MMR lambda: 0(다양성) ~ 1(관련성) trade-off
    mmr_lambda = st.slider("MMR lambda(관련성↔다양성)", 0.0, 1.0, 0.5, 0.05)
    # LLM Re-rank: 후보 chunk를 LLM으로 재정렬(정밀도↑ 비용/시간↑)
    use_rerank = st.checkbox("LLM Re-rank", value=True)
    # fetch_k: 초기 후보 수(많을수록 rerank/MMR에 유리하지만 계산량 증가)
    fetch_k = st.slider("fetch_k(후보 수)", 8, 80, 20, 4)

# --------------------------------------------
# 세션 상태 초기화: 앱 재실행/재렌더링 시에도 상태를 유지하기 위함
# --------------------------------------------
if "index_obj" not in st.session_state:
    # 임베딩/인덱스 객체(FAISS 없이 내부 구조로 brute-force 검색)
    st.session_state.index_obj = None
if "chunks" not in st.session_state:
    # 청킹 결과(각 chunk = {"text": ..., "meta": {...}} 형태 기대)
    st.session_state.chunks = []
if "index_meta" not in st.session_state:
    # 인덱스 구성 정보(출처, 청킹 파라미터, chunk 수 등)
    st.session_state.index_meta = None

# --------------------------------------------
# 인덱스 생성 로직: build_btn 클릭 시 실행
# --------------------------------------------
if build_btn:
    if not pages:
        # 입력 문서가 없으면 안내
        st.error("문서가 비어있습니다. PDF/URL/노트를 입력하세요.")
    else:
        try:
            # OpenAI 클라이언트 준비(키 검증 포함)
            client = get_client_from_session()

            # 페이지 텍스트를 chunk로 분할
            chunks = chunk_pages(pages, chunk_size=chunk_size, overlap=overlap)

            # 세션에 chunk 저장(미리보기/질의시 활용)
            st.session_state.chunks = chunks

            # chunk 임베딩을 계산하고 인덱스를 구성
            st.session_state.index_obj = build_index(client, chunks)

            # 현재 인덱스 설정을 메타로 저장(화면에 표시/재현성)
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
            # 로딩/청킹/임베딩 중 어떤 예외든 UI에 표시
            st.error(str(e))

# --------------------------------------------
# 메인 UI: 좌(질문/검색) + 우(chunk 미리보기)
# --------------------------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.header("4) 질문")

    # 인덱스가 존재하면 현재 인덱스 상태를 요약 표시
    if st.session_state.index_meta:
        m = st.session_state.index_meta
        st.info(
            f"현재 인덱스: pages={m['num_pages']} | chunks={m['num_chunks']} | "
            f"{m['mode']} | {m['source']} | chunk_size={m['chunk_size']} | overlap={m['overlap']}"
        )

    # 사용자의 자연어 질문 입력
    q = st.text_input("질문을 입력하세요", placeholder="예: RAG가 hallucination을 줄이는 원리는?")
    # top_k: 최종적으로 사용할 근거 chunk 개수
    top_k = st.slider("top_k", 1, 8, 4, 1)
    # 검색+응답 트리거
    ask = st.button("검색+응답")

with col2:
    st.header("Chunk 미리보기")
    chunks = st.session_state.chunks

    # 청킹 결과가 있으면 특정 chunk를 선택해 내용/메타 확인
    if chunks:
        st.write(f"총 {len(chunks)} chunks")
        idx = st.slider("미리볼 chunk_id", 0, len(chunks) - 1, 0, 1)
        # chunk 메타(출처, 페이지, chunk_id 등) 확인
        st.json(chunks[idx]["meta"])
        # chunk 텍스트 일부만 미리보기(너무 길면 UI 과부하 방지)
        st.code(chunks[idx]["text"][:1200])

# --------------------------------------------
# 질의 실행: ask 클릭 시 검색 → Evidence 표시 → RAG 답변 생성
# --------------------------------------------
if ask:
    if st.session_state.index_obj is None:
        # 인덱스 없이 검색하려 하면 안내
        st.error("먼저 인덱스를 생성하세요.")
    elif not q.strip():
        # 빈 질문 방지
        st.error("질문을 입력하세요.")
    else:
        try:
            client = get_client_from_session()

            # retrieve:
            # 1) (선택) query rewrite
            # 2) fetch_k 후보 검색
            # 3) (선택) MMR로 top_k 추리기
            # 4) (선택) LLM rerank로 재정렬
            # 반환: 검색에 사용된 query + (chunk, score) 리스트
            search_query, hits = retrieve(
                client,
                st.session_state.index_obj,
                q,
                top_k=top_k,
                fetch_k=fetch_k,
                use_rewrite=use_rewrite,
                use_mmr=use_mmr,
                mmr_lambda=mmr_lambda,
                use_rerank=use_rerank,
            )

            # rewrite된 검색 질의를 사용자에게 표시(디버깅/학습 목적)
            st.caption(f"검색용 질의(rewrite): {search_query}")

            # ----------------------------------------
            # Retrieved Evidence 출력: 근거 확인 UI
            # ----------------------------------------
            st.subheader("Retrieved Evidence")
            for i, (ch, score) in enumerate(hits, 1):
                meta = ch.get("meta", {})
                # source 표시 우선순위: 파일/URL/unknown
                src = meta.get("source") or meta.get("url") or "unknown"
                page = meta.get("page", "")
                cid = meta.get("chunk_id", "")
                title = f"[{i}] {src} p{page} c{cid} | score={score:.3f}"

                # expander로 chunk별 근거를 접었다 펼 수 있게 구성
                with st.expander(title):
                    st.json(meta)
                    st.write(ch.get("text", ""))

            # ----------------------------------------
            # LLM Answer: 근거(hits)를 함께 넣어 답변 생성
            # ----------------------------------------
            st.subheader("LLM Answer")
            ans = answer_with_rag(client, q, hits)
            st.write(ans)

        except Exception as e:
            # 검색/리랭크/답변 생성 중 예외 처리
            st.error(str(e))