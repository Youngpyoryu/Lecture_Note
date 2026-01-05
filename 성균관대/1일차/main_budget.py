# main_budget.py
import os
import csv
from datetime import datetime, date

import streamlit as st
from openai import OpenAI
from openai import AuthenticationError, RateLimitError, APIError

# =========================================
# 0) 실습 설정 (USD 기준) 
# =========================================
OPENAI_API_KEY = ""   # <-- key를 여기에 붙여넣기 
MODEL = "gpt-4o-mini" # 비용 실습은 mini 권장(저렴)
SESSION_BUDGET_USD = 20.0   # 3만원 ≈ $20 전후(환율 고정 가정)
DAILY_BUDGET_USD = 20.0     # 하루 1회 실습이면 session과 동일하게
MAX_REQUESTS_PER_SESSION = 80
MAX_INPUT_CHARS = 2000
MAX_OUTPUT_TOKENS = 256
LOG_PATH = "usage_log.csv"

# 모델 단가(USD / 1M tokens) - 최신 가격표 기준으로 유지
PRICING = {
    "gpt-4o-mini": {"in": 0.15, "in_cached": 0.08, "out": 0.60},
    "gpt-4o":      {"in": 2.50, "in_cached": 1.25, "out": 10.00},
}
# =========================================

def ensure_log_header():
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                "ts", "day", "model",
                "input_tokens", "cached_tokens", "output_tokens", "total_tokens",
                "cost_usd", "session_spent_usd", "day_spent_usd",
                "prompt_preview", "answer_preview"
            ])

def estimate_cost_usd(model: str, usage: dict) -> float:
    p = PRICING.get(model)
    if not p or not usage:
        return 0.0

    in_tok = int(usage.get("input_tokens", 0) or 0)
    out_tok = int(usage.get("output_tokens", 0) or 0)

    cached = 0
    itd = usage.get("input_tokens_details") or {}
    if isinstance(itd, dict):
        cached = int(itd.get("cached_tokens", 0) or 0)

    non_cached_in = max(in_tok - cached, 0)

    cost = (non_cached_in / 1_000_000) * p["in"]
    cost += (cached / 1_000_000) * p["in_cached"]
    cost += (out_tok / 1_000_000) * p["out"]
    return cost

def guardrail_check(prompt: str) -> str | None:
    if not prompt.strip():
        return "입력이 비어 있습니다."
    if len(prompt) > MAX_INPUT_CHARS:
        return f"입력이 너무 깁니다. (최대 {MAX_INPUT_CHARS}자)"
    if st.session_state.req_count >= MAX_REQUESTS_PER_SESSION:
        return f"세션 요청 횟수 한도 초과: {MAX_REQUESTS_PER_SESSION}회"

    # 날짜 변경 시 day_spent 초기화
    today = date.today().isoformat()
    if st.session_state.day != today:
        st.session_state.day = today
        st.session_state.day_spent_usd = 0.0

    if st.session_state.session_spent_usd >= SESSION_BUDGET_USD:
        return f"세션 예산 초과: ${SESSION_BUDGET_USD:.2f}"
    if st.session_state.day_spent_usd >= DAILY_BUDGET_USD:
        return f"일 예산 초과: ${DAILY_BUDGET_USD:.2f}"

    return None

# ---------------- UI ----------------
st.set_page_config(page_title="Budget Guardrail (USD)", layout="centered")
st.title("비용/토큰 로그 + Guardrail (USD)")

if not OPENAI_API_KEY.strip():
    st.error("상단 실습 설정에서 OPENAI_API_KEY를 입력하세요.")
    st.stop()

if "req_count" not in st.session_state:
    st.session_state.req_count = 0
if "session_spent_usd" not in st.session_state:
    st.session_state.session_spent_usd = 0.0
if "day_spent_usd" not in st.session_state:
    st.session_state.day_spent_usd = 0.0
if "day" not in st.session_state:
    st.session_state.day = date.today().isoformat()

client = OpenAI(api_key=OPENAI_API_KEY.strip())

st.caption(
    f"Model={MODEL} | session cap=${SESSION_BUDGET_USD:.2f} | daily cap=${DAILY_BUDGET_USD:.2f} | "
    f"max_out={MAX_OUTPUT_TOKENS} | max_req={MAX_REQUESTS_PER_SESSION}"
)

system = st.text_input("System", value="너는 간결하고 정확한 코딩 튜터야. 한국어로 답해.")
prompt = st.text_area("질문", height=140, placeholder="예) isinstance()가 뭐야? 예제도 같이.")

col1, col2 = st.columns(2)
send = col1.button("보내기", use_container_width=True)
reset = col2.button("세션 초기화", use_container_width=True)

if reset:
    st.session_state.req_count = 0
    st.session_state.session_spent_usd = 0.0
    st.success("세션 누적값을 초기화했습니다.")

st.write(
    f"- session spent: **${st.session_state.session_spent_usd:.2f} / ${SESSION_BUDGET_USD:.2f}**\n"
    f"- day spent: **${st.session_state.day_spent_usd:.2f} / ${DAILY_BUDGET_USD:.2f}**\n"
    f"- requests: **{st.session_state.req_count}/{MAX_REQUESTS_PER_SESSION}**"
)

if send:
    err = guardrail_check(prompt)
    if err:
        st.error(err)
        st.stop()

    try:
        r = client.responses.create(
            model=MODEL,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt.strip()},
            ],
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )

        answer = r.output_text or ""
        usage = r.usage.model_dump() if hasattr(r.usage, "model_dump") else (r.usage or {})

        cost_usd = estimate_cost_usd(MODEL, usage)

        # 누적 업데이트
        st.session_state.req_count += 1
        st.session_state.session_spent_usd += cost_usd
        st.session_state.day_spent_usd += cost_usd

        st.subheader("답변")
        st.write(answer)

        # 이번 요청 사용량
        in_tok = int(usage.get("input_tokens", 0) or 0)
        out_tok = int(usage.get("output_tokens", 0) or 0)
        total_tok = int(usage.get("total_tokens", 0) or 0)
        cached_tok = int((usage.get("input_tokens_details") or {}).get("cached_tokens", 0) or 0)

        st.subheader("이번 요청 사용량/비용(추정)")
        st.write(
            f"- input_tokens: **{in_tok}** (cached: {cached_tok})\n"
            f"- output_tokens: **{out_tok}**\n"
            f"- total_tokens: **{total_tok}**\n"
            f"- estimated cost: **${cost_usd:.6f}**"
        )

        # 로그 저장
        ensure_log_header()
        with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                datetime.now().isoformat(timespec="seconds"),
                st.session_state.day,
                MODEL,
                in_tok, cached_tok, out_tok, total_tok,
                f"{cost_usd:.8f}",
                f"{st.session_state.session_spent_usd:.6f}",
                f"{st.session_state.day_spent_usd:.6f}",
                prompt[:120].replace("\n", " "),
                answer[:120].replace("\n", " "),
            ])

        st.success(f"로그 저장: {LOG_PATH}")

    except AuthenticationError as e:
        st.error("401 인증 실패: API 키/프로젝트 문제")
        st.caption(str(e))
    except RateLimitError as e:
        st.error("429 한도/결제 문제: billing 또는 rate limit")
        st.caption(str(e))
    except APIError as e:
        st.error("API 오류")
        st.caption(str(e))
    except Exception as e:
        st.error("알 수 없는 오류")
        st.caption(str(e))
