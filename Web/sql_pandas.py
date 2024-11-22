import pymysql
import pandas as pd

# MySQL 연결 설정
def connect_to_mysql():
    return pymysql.connect(
        host="localhost",       # MySQL 호스트
        user="root",            # MySQL 사용자
        password="1234",        # MySQL 비밀번호
        database="melon_chart", # 사용할 데이터베이스
        charset="utf8mb4",      # 한글 지원
        port=3306               # 포트 번호
    )

# SQL 쿼리 결과를 Pandas DataFrame으로 가져오기
def fetch_data():
    connection = connect_to_mysql()  # MySQL 연결
    try:
        query = "SELECT * FROM chart;"  # 원하는 SQL 쿼리
        df = pd.read_sql(query, connection)  # Pandas로 결과 가져오기
        return df
    except pymysql.MySQLError as e:
        print(f"Error fetching data from MySQL: {e}")
        return None
    finally:
        connection.close()  # 연결 닫기

# 데이터를 가져와서 출력
df = fetch_data()
if df is not None:
    print(df.head())  # DataFrame의 앞부분 출력
else:
    print("No data fetched.")
