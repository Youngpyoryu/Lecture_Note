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
    - 예외 종류: `ValueError`, `TypeError`, `ZeroDivisionError`  
    - 사용자 정의 예외 클래스  

- 실습 예제 (Practice) / 답안은 수업시간에만 공개됩니다.
    - 구구단 출력  
    - 리스트 평균 및 최대값 구하기  
    - 문자열 단어 빈도 계산기  
