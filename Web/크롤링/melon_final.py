import requests
from bs4 import BeautifulSoup
import pymysql
import time

# MySQL 연결 설정
def connect_to_mysql():
    return pymysql.connect(
        host="localhost",       # MySQL 호스트 (예: "127.0.0.1")
        user="root",            # MySQL 사용자
        password="1234",  # MySQL 비밀번호
        database="melon_chart", # 사용할 데이터베이스
        charset="utf8mb4"       # 한글 지원
    )

# 크롤링 함수
def scrape_melon_chart():
    url = "https://www.melon.com/chart/index.htm"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch Melon Chart: Status Code {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # 곡명, 아티스트 데이터 추출
        titles_raw = soup.select('div.ellipsis.rank01 a')  # 곡명
        artists_raw = soup.select('div.ellipsis.rank02 span')  # 아티스트

        # 순위 데이터 필터링
        ranks_raw = [rank.text.strip() for rank in soup.select('span.rank')]
        ranks = [int(rank) for rank in ranks_raw if rank.isdigit()]  # 숫자만 필터링

        # 데이터 병합
        chart_data = []
        for i in range(len(titles_raw)):
            try:
                chart_data.append({
                    'rank': ranks[i],  # 순위
                    'title': titles_raw[i].text.strip(),  # 곡명
                    'artist': artists_raw[i].text.strip()  # 아티스트
                })
            except IndexError as e:
                print(f"Skipping invalid rank: {ranks_raw[i]} - Error: {e}")
            except Exception as e:
                print(f"Error processing entry {i}: {e}")

        time.sleep(3)  # 요청 간격 조절
        return chart_data

    except Exception as e:
        print(f"Error during scraping: {e}")
        return []

# MySQL에 데이터 저장 함수
def save_to_mysql(data):
    connection = connect_to_mysql()  # MySQL 연결
    try:
        with connection.cursor() as cursor:
            # 데이터를 테이블에 삽입
            for item in data:
                sql = """
                INSERT INTO chart (`rank`, title, artist)
                VALUES (%s, %s, %s)
                """
                cursor.execute(sql, (item['rank'], item['title'], item['artist']))
            connection.commit()  # 변경사항 저장
        print("Data successfully saved to MySQL.")
    except pymysql.MySQLError as e:
        print(f"Error saving data to MySQL: {e}")
    finally:
        connection.close()  # 연결 닫기

# 크롤링 실행 및 데이터 저장
if __name__ == "__main__":
    chart_data = scrape_melon_chart()
    if chart_data:
        save_to_mysql(chart_data)
    else:
        print("No data fetched.")
