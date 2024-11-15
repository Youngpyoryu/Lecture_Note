from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By  #find_element 함수 쉽게 쓰기 위함.
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time

chrome_options = Options()
chrome_options.add_experimental_option("detach",True)
chrome_options.add_argument("lang=ko_KR") #한국어

# colab에서 selenium을 돌리기 위한 옵션들
chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=chrome_options)

#11번가 이동
driver.get('https://www.11st.co.kr/browsing/BestSeller.tmall?method=getBestSellerMain&xfrom=main^gnb')

#스크롤 다운
SCROLL_PAUSE_SEC = 1

#스크롤 높이 가져옴.
last_height = driver.execute_script('return document.body.scrolHeight')

while True:
    #끝까지 스크롤 다운
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

    #1초 대기
    time.sleep(SCROLL_PAUSE_SEC)

    #스크롤 다운 후 스크롤 높이 다시 가져옴
    new_height = driver.execute_script('return document.body.scrollHeight')
    if new_height == last_height:
        break
    last_height = new_height

#데이터를 저장할 리스트 생성
all_data = []

#best의 순번을 가지고 오자! ex)1위,2위,3위....500등

try:
    lists = driver.find_element(By.ID,'bestPrdList').find_element(By.CLASS_NAME,'viewtype')
    #li 태그를 가져오자
    for list in lists:
        bestlist = list.find_elements(By.TAG_NAME, 'li')
        for item in bestlist:
            try:    
                rank = item.find_element(By.CLASS_NAME, 'best').text #순번
                product_name = item.find_element(By.CLASS_NAME, 'pname').find_element(By.TAG_NAME, 'p').text #제품명
                price = item.find_element(By.CLASS_NAME, 'sale_price').text #가격
                product_url = item.find_element(By.CLASS_NAME, 'box_pd.ranking_pd').find_element(By.TAG_NAME, 'a').get_attribute('href') #URL 추
                #중간에 스페이스 태그로 되어있는 것은 .으로 연결이 가능함.
                image_url = item.find_element(By.CLASS_NAME,'img_plot').find_element(By.TAG_NAME,'img').get_attribute('src')

                #수집한 데이터를 딕셔너리 형태로 리스트에 추가.
                all_data.append({
                    "Rank" : rank,
                    "Product Name":product_name,
                    "Price" : price,
                    "Product URL":product_url,
                    "Image URL": image_url
                })
            except NoSuchElementException:
                print('An element was not found in this item.')
except NoSuchElementException:
    print('The product list was not found.')

df = pd.DataFrame(all_data)
print(df.head())
df.to_csv('./')

        
        