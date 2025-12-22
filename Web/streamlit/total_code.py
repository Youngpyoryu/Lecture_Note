# Streamlit 체계적으로 배우기 위한 전체 코드 예제

import streamlit as st
import pandas as pd
import numpy as np

# 앱의 타이틀과 설명
st.title('Streamlit 체계적 학습 가이드')
st.write('이 앱을 통해 Streamlit의 기본부터 다양한 기능까지 체계적으로 배울 수 있습니다.')

# 섹션 1: 기본 텍스트 및 타이틀 표시
st.header('1. 기본 텍스트 및 타이틀 표시하기')
st.subheader('부제목 표시하기')
st.write('일반 텍스트는 st.write로 간단히 표시합니다.')

# 섹션 2: 인터랙티브 버튼과 체크박스
st.header('2. 인터랙티브 버튼과 체크박스 사용하기')
if st.button('클릭하세요!'):
    st.success('버튼을 클릭했습니다!')

check = st.checkbox('체크박스 선택하기')
if check:
    st.info('체크박스가 선택되었습니다.')

# 섹션 3: 사용자 입력 위젯 (슬라이더, 셀렉트박스 등)
st.header('3. 사용자 입력 위젯 활용하기')
age = st.slider('나이 선택:', 0, 100, 25)
color = st.selectbox('좋아하는 색상을 고르세요:', ['빨강', '파랑', '초록'])
st.write(f'나이는 {age}세, 좋아하는 색상은 {color}입니다.')

# 섹션 4: 데이터프레임과 차트 시각화하기
st.header('4. 데이터프레임과 차트 시각화하기')
data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['A', 'B', 'C']
)

st.write('데이터프레임 예시:', data)
st.line_chart(data)

# 섹션 5: 사이드바 및 레이아웃 관리하기
st.header('5. 사이드바 및 레이아웃 관리')
st.sidebar.title('사이드바 메뉴')
menu = st.sidebar.radio('메뉴 선택', ['홈', '데이터 분석', '설정'])
st.write('선택한 메뉴:', menu)

col1, col2 = st.columns(2)
with col1:
    st.write('왼쪽 컬럼 내용입니다.')
with col2:
    st.write('오른쪽 컬럼 내용입니다.')

# 섹션 6: 파일 업로드와 이미지 표시
st.header('6. 파일 업로드와 이미지 표시하기')
uploaded_file = st.file_uploader('파일 업로드')
if uploaded_file:
    st.image(uploaded_file)

# 섹션 7: 고급 예제 (세션 상태 유지)
st.header('7. 고급 예제: 세션 상태 유지하기')

if 'counter' not in st.session_state:
    st.session_state.counter = 0

increment = st.button('카운터 증가')
if increment:
    st.session_state.counter += 1

st.write('현재 카운터 값:', st.session_state.counter)
