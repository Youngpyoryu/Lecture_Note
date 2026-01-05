# main_tools.py
import os, json, ast, operator as op
import streamlit as st
from openai import OpenAI
from openai import AuthenticationError, RateLimitError, APIError

# =========================
# 0) 실습 설정
# =========================
OPENAI_API_KEY = ""  # API key 기입
MODEL = "gpt-4o-mini"
MAX_OUTPUT_TOKENS = 400
# =========================

# -------------------------
# 1) 안전한 "계산기" (eval 금지)
# -------------------------
_ALLOWED_OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.Pow: op.pow, ast.USub: op.neg, ast.UAdd: op.pos,
    ast.Mod: op.mod, ast.FloorDiv: op.floordiv,
}

def safe_calc(expression: str) -> float:
    """
    허용: 숫자, + - * / ** ( ) % //  .  (지수표기 1e-3 가능)
    금지: 함수호출, 변수, 인덱싱 등
    """
    if len(expression) > 200:
        raise ValueError("Expression too long (max 200 chars).")

    node = ast.parse(expression, mode="eval")

    def _eval(n):
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in _ALLOWED_OPS:
            return _ALLOWED_OPS[type(n.op)](_eval(n.left), _eval(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _ALLOWED_OPS:
            return _ALLOWED_OPS[type(n.op)](_eval(n.operand))
        raise ValueError("Disallowed expression.")

    return float(_eval(node))

# -------------------------
# 2) JSON 검증기
# -------------------------
def validate_json(text: str) -> dict:
    if len(text) > 50_000:
        return {"valid": False, "error": "JSON too large (max 50KB)."}
    try:
        obj = json.loads(text)
        return {"valid": True, "error": None, "parsed_type": type(obj).__name__}
    except json.JSONDecodeError as e:
        return {"valid": False, "error": f"{e.msg} (line {e.lineno}, col {e.colno})"}

# -------------------------
# 3) Tools 스키마(함수 인터페이스)
# -------------------------
TOOLS = [
    {
        "type": "function",
        "name": "calc_expression",
        "description": "Evaluate a pure arithmetic expression safely. No variables, no functions.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Arithmetic expression, e.g., (3.2e-4*5.7e3)/9.1"}
            },
            "required": ["expression"],
        },
    },
    {
        "type": "function",
        "name": "validate_json",
        "description": "Validate whether a string is valid JSON. Return error location if invalid.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "JSON string to validate"}
            },
            "required": ["text"],
        },
    },
]

# -------------------------
# 4) 함수 호출 처리 루프
# -------------------------
def run_agent(client: OpenAI, user_text: str) -> str:
    """
    Responses API: tools 포함 요청 → function_call 처리 → function_call_output 추가 → 최종 답변
    """
    input_list = [
        {"role": "system", "content": "너는 도구를 사용할 수 있는 조교야. 필요하면 도구를 호출해 정확히 답해. 한국어로 답해."},
        {"role": "user", "content": user_text},
    ]

    while True:
        resp = client.responses.create(
            model=MODEL,
            tools=TOOLS,
            input=input_list,
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )

        # 모델 출력 item들을 input_list에 누적(다음 턴 컨텍스트)
        input_list += resp.output

        tool_calls = [it for it in resp.output if getattr(it, "type", None) == "function_call"]
        if not tool_calls:
            return resp.output_text or ""

        # function_call 처리
        for call in tool_calls:
            name = call.name
            args = json.loads(call.arguments or "{}")

            if name == "calc_expression":
                try:
                    value = safe_calc(args["expression"])
                    out = {"ok": True, "value": value}
                except Exception as e:
                    out = {"ok": False, "error": str(e)}

            elif name == "validate_json":
                out = validate_json(args["text"])

            else:
                out = {"ok": False, "error": f"Unknown tool: {name}"}

            # tool output을 call_id에 연결해서 다시 모델에게 제공 :contentReference[oaicite:1]{index=1}
            input_list.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(out, ensure_ascii=False),
            })

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="Tool-Calling Chatbot", layout="centered")
st.title("함수 호출 맛보기: 계산기 / JSON 검증기")

api_key = st.text_input("OpenAI API Key", value=OPENAI_API_KEY, type="password", placeholder="sk-proj-...")
q = st.text_area("입력", height=140, placeholder="예) (3.2e-4*5.7e3)/9.1 계산해줘\n예) 이 JSON 맞아? {\"a\":1,}")

if st.button("실행"):
    if not api_key.strip():
        st.error("API Key를 입력하세요.")
        st.stop()

    client = OpenAI(api_key=api_key.strip())

    try:
        ans = run_agent(client, q.strip())
        st.subheader("출력")
        st.write(ans)

    except AuthenticationError as e:
        st.error("401 인증 실패")
        st.caption(str(e))
    except RateLimitError as e:
        st.error("429 한도/결제/레이트리밋")
        st.caption(str(e))
    except APIError as e:
        st.error("API 오류")
        st.caption(str(e))
    except Exception as e:
        st.error("알 수 없는 오류")
        st.caption(str(e))
