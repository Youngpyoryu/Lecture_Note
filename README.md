# 수리중(2025.08.01 ~)


## 1. Python 기초 강의 정리

- Python 소개
    - Python의 특징과 장점  
    - 인터프리터 구조, 실행 방식  
    - 개발 환경: Jupyter Notebook / VSCode / Google Colab  

- 기본 문법 (Syntax)
    - 들여쓰기(indentation)와 코드 블록  
    - 변수 선언 및 자료형 자동 추론  
    - 주석(`'#'`)과 문자열 내 따옴표 처리  
    - `print()`로 문자열 포매팅 (f-string, format, %)  

- 데이터 타입 (Data Types)
    - 숫자형: `int`, `float`, `complex`  
    - 문자열(`str`): 슬라이싱, 인덱싱, 메서드(`split`, `join`, `replace`)   
    - 불리언(`bool`), NoneType  
    - 타입 변환: `int()`, `str()`, `float()`  

- 연산자 (Operators)
    - 산술: `+ - * / // % **`  
    - 비교: `== != > < >= <=`  
    - 논리: `and`, `or`, `not`  
    - 대입: `= += -= *=`  
    - 멤버·식별 연산자: `in`, `not in`, `is`  
- 조건문 (Conditionals)
    - `if`, `elif`, `else` 구문  
    - 중첩 조건문 및 한 줄 조건식 (삼항 연산자)  
    - 예제: 성적 등급 분류기  

- 반복문 (Loops)
    - `for` 루프: `range()`, 리스트 순회  
    - `while` 루프: 조건 기반 반복  
    - 제어문: `break`, `continue`, `pass`  
    - 리스트 내포(List Comprehension)  


-  컬렉션 자료형 (Collections)
    - 리스트(List): 인덱싱, 슬라이싱, 추가/삭제 (`append`, `remove`)  
    - 튜플(Tuple): 불변(immutable) 특성  
    - 딕셔너리(Dictionary): `key:value` 구조, `.keys()`, `.values()`  
    - 세트(Set): 집합 연산 (합집합, 교집합, 차집합)  
    - 얕은 복사 vs 깊은 복사  

- 함수 (Functions)
    - 함수 정의와 호출 (`def`, `return`)  
    - 인자 전달 방식: 위치/기본값/가변(`*args`, `**kwargs`)  
    - 람다 함수 (익명 함수)  
    - 지역변수와 전역변수(scope)  
    - 함수형 프로그래밍(`map`, `filter`, `reduce`)  

- 모듈 & 패키지 (Modules & Packages)
    - `import`, `from ... import ...`  

- 파일 입출력 (File I/O)
    - `open()`, `read()`, `write()`, `close()`  
    - `with open() as f:` 문으로 안전하게 처리  
    - 파일 모드(`r`, `w`, `a`, `rb`, `wb`)  
    - CSV 파일 다루기 (`split`, `strip`, `csv` 모듈)  

-  예외 처리 (Exception Handling)
    - `try`, `except`, `else`, `finally` 구조  
    - 예외 종류: `ValueError`, `TypeError`
    - 사용자 정의 예외 클래스  

- 실습 예제 (Practice) / 답안은 수업시간에만 공개됩니다.
    - 구구단 출력  
    - 리스트 평균 및 최대값 구하기  
    - 문자열 단어 빈도 계산기
 

<동적크롤링>
- API를 활용한 정적크롤링(다음, 네이버, 카카오, 한국영화)
- 2018년도부터 2022년까지 영화 best 5 영화 이미지 가져오기
- 11번가 동적 크롤링
- 쿠팡 동적 크롤링

<빅데이터를 위한 수학>
1. 고등학교 수학
 - 집합, 함수, 수열, 급수, 극한, 연속, 평균변화율, 미분, 확률

2. 선형대수학
- 선형성, 벡터의 연산, 행렬의 연산, 특수한 형태의 행렬, 선형결합, 생성(span), 일차독립, 일차종속, 기저(basis), 차원과 rank, 선형 시스템,소거법, 행렬변환, 역행렬, 행렬 분해, 내적, 내적의 크기, 벡터의 크기, 벡터의 정사영, Least-Square Solution, 고윳값과 고유벡터, 대각화, SVD

3. 미적분학
- 미분, 미분가능성, 접선의 방정식, 최대&최소, 극대&극소, 미분 불가능, 롤의 정리, 평균값 정리, 뉴턴법, 편도함수, 합성함수의 미분법, 연쇄법칙, 편미분, 방향도함수, Taylor 정리

4. 통계학
- 통계분석의 이해, 모집단, 모수, 표본집단, 통계량, 표본 추출방법, 측정, 확률정의, 확률변수의 기댓값, 적률, 평균과 분산, 중위수, 최빈값, 이상치, 왜도, 첨도, 독립사건, 배반사건, 이산형 확률분포, 연속형 확률분포, 자유도, 점 추정, 구간 추정, 가설검정, 유의확률(p-value), 큰 수의 법칙, 중심극한정리, 산점도, 공분산, 상관계수,  빈도주의 VS 베이지안 관점, 확률분포의 관계도

<머신러닝: 회귀>
- 회귀란? , 지도학습의 종류, 경사하강법, 상관계수, 결정계수, adjusted-R2, AIC,BIC, 다중회귀분석, lasss, Ridge, Elasticnet,  우도(likelihood), t-통계량, F-통계량, 가설검정, dubin-watson, Jarque-Bera 

- 실습 : statsmodels  / bike-sharing meand kaggle데이터로 시계열 데이터접근을 함.

<시계열 분석>
- 시계열 자료, 데이터관점에 따른 분류, 정상성과 비정상성의 구분, 시계열의 구성 요인, 정상성 확보, 통계적 특성, 확률과정(Markov process, markov chain), 정상시계열 전환의 목적, 자기공분산, 자기상관계수
- 모델: MA, AR, 평활화, ARIMA -> ARIMA 계열 및Generalized Autoregressive Conditional Heteroskedasticity
<머신러닝 분류>
- 오분류표, 의사결정나무, 엔트로피 함수, Gradient boosting, ada boosting, XGBOOST, LIGHTGBM, CATBOOST, 앙상블(Bagging, voting, Boosting, Stacking)

<머신러닝 비지도 학습>
- PCA, LLE, Manifold Learning, NMF, LDA, QDA, K-menas , K-centeroid, K-Prototypes, MEan Shift, GMM clstering, DBSCAN, OPTICS, Yellowbrick X Kneed
 -> Customer Personality Analysis (Kaggle Dataset)

<딥러닝>
- 뉴런, 뉴런의 수학적 작동, 초기값 설정방법, optimizer, perceptron, CNN, RNN, LSTM, GRU, Transformer 

