#main.py
import os
import streamlit as st
from openai import OpenAI
from openai import AuthenticationError, RateLimitError, APIError

st.set_page_config(page_title="Q&A (Streamlit + OpenAI)", layout="centered")
st.title("질문 → 답변 (Streamlit + OpenAI)")

# 1) API Key: 환경변수 OPENAI_API_KEY 우선
default_key = (os.environ.get("OpenAPI-key") or "").strip()

api_key = st.text_input(
    "OpenAPI-key",
    value=default_key,
    type="password",
    placeholder="sk-proj-...",
)

MODEL = st.selectbox("Model", ["gpt-4-0613", "gpt-4o"], index=0)
system = st.text_input("System", value="너는 간결하고 정확한 코딩 튜터야. 한국어로 답해.")
q = st.text_area("질문", height=120, placeholder="예) isinstance()가 뭐야? 예제도 같이.")
send = st.button("보내기")

if send:
    if not api_key.strip():
        st.error("API Key가 필요합니다. 환경변수 OPENAI_API_KEY를 설정하거나 위에 입력하세요.")
        st.stop()

    client = OpenAI(api_key=api_key.strip())

    try:
        r = client.responses.create(
            model=MODEL,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": q.strip()},
            ],
        )
        st.subheader("답변")
        st.write(r.output_text)

    except AuthenticationError as e:
        st.error("401 인증 실패: API 키/프로젝트 설정 문제입니다.")
        st.caption(str(e))
    except RateLimitError as e:
        st.error("429 한도/결제 문제: billing 또는 rate limit 이슈입니다.")
        st.caption(str(e))
    except APIError as e:
        st.error("API 오류(요청/서버 오류)")
        st.caption(str(e))
    except Exception as e:
        st.error("알 수 없는 오류")
        st.caption(str(e))
