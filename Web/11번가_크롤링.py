from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By #find_element 함수를 쉽게 쓰기위함.
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import sys
import pandas as pd
sys.stdout.reconfigure(encoding = 'utf-8')

chrome_options = Options()
chrome_options.add_experimental_option("detach",True)
chrome_options.add_argument("--lang=ko_KR")

driver = webdriver.Chrome(options= chrome_options)
driver.get('https://www.11st.co.kr/browsing/BestSeller.tmall?method=getBestSellerMain&xfrom=main^gnb')

SCROLL_PAUSE_SEC = 1
last_height = driver.execute_script('return document.body.scrollHeight')

while True:
    driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
    time.sleep(SCROLL_PAUSE_SEC)
    new_height = driver.execute_script('return document.body.scrollHeight')
    if new_height == last_height:
        break
    last_height = new_height

all_data = []

try:
    lists = driver.find_element(By.ID, 'bestPrdList').find_elements(By.CLASS_NAME,'viewtype')

    for list in lists :
        bestlist = list.find_elements(By.CLASS_NAME,'box_pd')
        try:
            for item in bestlist:
                rank = item.find_element(By.CLASS_NAME,'best').text
                product_name =  item.find_element(By.CLASS_NAME,'pname').find_element(By.TAG_NAME,'p').text
                price = item.find_element(By.CLASS_NAME,'sale_price').text
                product_url = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
                image_url = item.find_element(By.CLASS_NAME, 'img_plot').find_element(By.TAG_NAME, 'img').get_attribute('src')

                all_data.append ({
                    "Rank": rank,
                    "Product Name" : product_name,
                    "Price" : price,
                    "Product_URL" : product_url
                    ,"Image URL" : image_url
                })
        except NoSuchElementException:
            print("해당 항목 없음")
except NoSuchElementException:
    print("해당 항목 없음")

df = pd.DataFrame(all_data)
print(df.head())
