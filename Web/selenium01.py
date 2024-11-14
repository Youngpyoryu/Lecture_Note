from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By  #find_element 함수 쉽게 쓰기 위함.
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
chrome_options.add_experimental_option("detach",True)
chrome_options.add_argument("lang=ko_KR") #한국어

driver = webdriver.Chrome(options = chrome_options)
driver.get('https://www.google.com')
# search_box = driver.find_element(By.NAME,'q')
# search_box.send_keys('아이유')
# #"google 검색" 버튼이 클릭 가능할 때까지 대기 후 클릭.
# search_button = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.NAME,'btnK')))
# search_button.click()

driver.find_element(By.CLASS_NAME, "gLFyf").send_keys("아이유")
# driver.find_element(By.CLASS_NAME,"gLFyf").send_keys(Keys.ENTER)
# driver.find_element(By.CSS_SELECTOR,"body > div.L3eUgb > div.o3j99.ikrT4e.om7nvf > form > div:nth-child(1) > div.A8SBwf > div.FPdoLc.lJ9FBc > center > input.gNO89b").click()
driver.find_element(By.XPATH,"/html/body/div[1]/div[3]/form/div[1]/div[1]/div[4]/center/input[1]").click()
driver.find_element(By.XPATH,'//*[@id="hdtb-sc"]/div/div/div[1]/div/div[3]/a').click()


titles = []
links = driver.find_elements(By.CSS_SELECTOR,'.n0jPhd.ynAwRc.MBeuO.nDgy9d')
for link in links:
    titles.append(link.text)

print(titles)