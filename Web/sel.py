
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# WebDriver 설정 (Chrome)
driver = webdriver.Chrome()

# Google 이미지 검색 페이지 열기
driver.get("https://www.google.com/imghp")  # Google 이미지 검색 페이지

# 검색어 입력
search_box = driver.find_element(By.NAME, "q")
search_box.send_keys("아이유")  # 원하는 검색어 입력 (예: 아이유)
search_box.submit()  # 검색 실행

# 페이지 로딩 대기 (이미지 로딩을 위해 잠시 대기)
time.sleep(3)

# 이미지 요소 찾기
images = driver.find_elements(By.TAG_NAME, "img")

# 이미지 URL을 담을 리스트 초기화
image_urls = []

# 각 이미지에서 URL 추출
for image in images:
    try:
        # 이미지의 src 속성 가져오기
        img_url = image.get_attribute("src")
        if img_url:
            image_urls.append(img_url)  # URL 리스트에 추가
    except Exception as e:
        print(f"Error: {e}")

# 가져온 이미지 URL 출력
for img_url in image_urls:
    print(img_url)

# WebDriver 종료
driver.quit()