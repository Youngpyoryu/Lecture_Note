from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

URL = "https://huggingface.co/papers/trending"

def main():
    opts = Options()
    opts.add_argument("--headless=new")
    driver = webdriver.Chrome(options=opts)  # chromedriver 문제로 흔히 실패

    driver.get(URL)
    time.sleep(3)

    print("final url:", driver.current_url)
    print("title:", repr(driver.title))
    print("html head:", driver.page_source[:300].replace("\n", " "))

    driver.quit()

if __name__ == "__main__":
    main()
