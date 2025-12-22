# app.py
import streamlit as st
import pandas as pd
import numpy as np

# 앱 타이틀
st.title("Streamlit 고급 기능 실습")
st.write("다양한 Streamlit 기능을 심도 있게 배우기 위한 앱입니다.")

# 섹션 1: 인터랙티브 위젯 활용
st.header("1. 인터랙티브 위젯 활용하기")
name = st.text_input("이름을 입력하세요:")
age = st.number_input("나이를 입력하세요:", min_value=0, max_value=120)

if st.button("입력 완료"):
    st.success(f"{name}님의 나이는 {age}세 입니다.")

# 섹션 2: 고급 레이아웃 구성
st.header("2. 고급 레이아웃 구성하기")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("컬럼 1")
    st.write("첫 번째 컬럼입니다.")

with col2:
    st.subheader("컬럼 2")
    st.write("두 번째 컬럼입니다.")

with col3:
    st.subheader("컬럼 3")
    st.write("세 번째 컬럼입니다.")

# 섹션 3: 다양한 시각화 차트
st.header("3. 다양한 데이터 시각화하기")
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=["A", "B", "C"]
)
st.line_chart(chart_data)
st.bar_chart(chart_data)

# 섹션 4: 파일 처리 및 다운로드
st.header("4. 파일 업로드 및 다운로드하기")
uploaded_file = st.file_uploader("파일 업로드", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.dataframe(df, use_container_width=True)

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="CSV로 다운로드",
        data=csv_bytes,
        file_name="data.csv",
        mime="text/csv",
    )

# 섹션 5: 세션 상태와 고급 상태 관리
st.header("5. 세션 상태 및 고급 상태 관리")

if "counter" not in st.session_state:
    st.session_state["counter"] = 0

increment = st.button("카운터 증가")
reset = st.button("카운터 리셋")

if increment:
    st.session_state["counter"] += 1
if reset:
    st.session_state["counter"] = 0

st.write("현재 카운터 값:", st.session_state["counter"])

# 섹션 6: 페이지 네비게이션
st.header("6. 멀티페이지 네비게이션 예시")
page = st.sidebar.radio("페이지 선택", ["홈", "분석", "시각화"])

if page == "홈":
    st.write("홈 화면입니다.")
elif page == "분석":
    st.write("데이터 분석 페이지입니다.")
elif page == "시각화":
    st.write("시각화 페이지입니다.")

# 섹션 7: 멀티미디어 활용
st.header("7. 멀티미디어 요소 추가")
st.image(
    "https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png",
    width=300,
)
st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")

# 섹션 8: 캐싱 및 성능 최적화
st.header("8. 데이터 캐싱 및 성능 최적화")

@st.cache_data
def expensive_computation(n: int) -> int:
    return sum(i**2 for i in range(n))

num = st.slider("계산할 숫자 범위 선택:", 10_000, 1_000_000, step=10_000)
result = expensive_computation(num)
st.write(f"결과: {result}")
