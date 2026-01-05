# main_docqa.py
import os
import math
import streamlit as st
from openai import OpenAI
from openai import AuthenticationError, RateLimitError, APIError

# =========================================
# 0) 실습 설정 (USD 기준)
# =========================================
OPENAI_API_KEY = ""  # 시연용: 여기 붙여넣기 (공유/업로드 전 반드시 삭제)
MODEL_TEXT = "gpt-4o-mini"  # 텍스트 요약/질의용(저렴)
MODEL_PDF = "gpt-4o"        # PDF 입력 지원 모델(가이드 참고) :contentReference[oaicite:5]{index=5}

MAX_OUTPUT_TOKENS = 300
TXT_MAX_CHARS_DIRECT = 12000      # 이 이하이면 원문을 바로 컨텍스트에 포함
TXT_CHUNK_CHARS = 4000            # chunk 요약 단위
# =========================================

st.set_page_config(page_title="Doc → Summary/Q&A", layout="centered")
st.title("파일 업로드 → 요약/질의 실습")

if not OPENAI_API_KEY.strip():
    st.error("상단 '# 0) 실습 설정'에서 OPENAI_API_KEY를 입력하세요.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY.strip())

mode = st.selectbox("모드", ["요약", "문서 기반 Q&A"], index=0)
uploaded = st.file_uploader("파일 업로드 (txt / pdf)", type=["txt", "pdf"])

system = st.text_input("System", value="너는 간결하고 정확한 조교야. 한국어로 답해.")
question = st.text_area("질문(요약 모드면 비워도 됨)", height=100, placeholder="예) 이 문서의 핵심 주장 3개만 요약해줘.")

run = st.button("실행")

def call_model_with_text(context_text: str, user_text: str) -> str:
    r = client.responses.create(
        model=MODEL_TEXT,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"[문서]\n{context_text}\n\n[요청]\n{user_text}"},
        ],
        max_output_tokens=MAX_OUTPUT_TOKENS,
    )
    return r.output_text or ""

def summarize_long_text(full_text: str) -> str:
    chunks = [full_text[i:i+TXT_CHUNK_CHARS] for i in range(0, len(full_text), TXT_CHUNK_CHARS)]
    st.caption(f"텍스트가 길어 {len(chunks)}개 chunk로 나누어 요약합니다.")
    partials = []
    for idx, ch in enumerate(chunks, start=1):
        partial = call_model_with_text(
            ch,
            "이 chunk의 핵심을 5줄 이내 bullet로 요약해줘."
        )
        partials.append(f"- chunk {idx}\n{partial}")
    merged = "\n\n".join(partials)
    final = call_model_with_text(
        merged,
        "위 chunk 요약들을 종합해 전체 문서 요약(핵심 5개 bullet + 한줄 결론)로 정리해줘."
    )
    return final

if run:
    if not uploaded:
        st.error("파일을 업로드하세요.")
        st.stop()

    try:
        # ---------------- TXT ----------------
        if uploaded.name.lower().endswith(".txt"):
            text = uploaded.read().decode("utf-8", errors="ignore").strip()

            if mode == "요약":
                if len(text) <= TXT_MAX_CHARS_DIRECT:
                    ans = call_model_with_text(text, "이 문서를 핵심 5개 bullet로 요약하고, 마지막에 한줄 결론을 써줘.")
                else:
                    ans = summarize_long_text(text)
                st.subheader("요약 결과")
                st.write(ans)

            else:  # 문서 기반 Q&A
                if not question.strip():
                    st.error("질문을 입력하세요.")
                    st.stop()

                if len(text) <= TXT_MAX_CHARS_DIRECT:
                    context = text
                else:
                    context = summarize_long_text(text)  # 긴 문서는 요약본을 컨텍스트로 사용

                ans = call_model_with_text(context, question.strip())
                st.subheader("답변")
                st.write(ans)

        # ---------------- PDF ----------------
        else:
            # Files API 업로드 후 file_id로 질문/요약 :contentReference[oaicite:6]{index=6}
            file_obj = client.files.create(
                file=(uploaded.name, uploaded.getvalue(), "application/pdf"),
                purpose="user_data",
            )

            if mode == "요약":
                prompt = question.strip() or "이 PDF의 핵심 내용을 7줄 이내로 요약해줘."
                r = client.responses.create(
                    model=MODEL_PDF,
                    input=[{
                        "role": "user",
                        "content": [
                            {"type": "input_file", "file_id": file_obj.id},
                            {"type": "input_text", "text": prompt},
                        ],
                    }],
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                )
                st.subheader("요약 결과")
                st.write(r.output_text or "")

            else:
                if not question.strip():
                    st.error("질문을 입력하세요.")
                    st.stop()
                r = client.responses.create(
                    model=MODEL_PDF,
                    input=[{
                        "role": "user",
                        "content": [
                            {"type": "input_file", "file_id": file_obj.id},
                            {"type": "input_text", "text": question.strip()},
                        ],
                    }],
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                )
                st.subheader("답변")
                st.write(r.output_text or "")

            st.caption("참고: PDF 입력은 페이지 이미지까지 포함되어 토큰/비용이 커질 수 있습니다. 대규모/다중 PDF는 RAG(file_search)로 전환하는 것이 안전합니다.")
    except AuthenticationError as e:
        st.error("401 인증 실패: API 키/프로젝트 설정 문제")
        st.caption(str(e))
    except RateLimitError as e:
        st.error("429 한도/결제/레이트리밋 문제")
        st.caption(str(e))
    except APIError as e:
        st.error("API 오류")
        st.caption(str(e))
    except Exception as e:
        st.error("알 수 없는 오류")
        st.caption(str(e))
