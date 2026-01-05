import time
import requests
from bs4 import BeautifulSoup

BASE = "https://arxiv.org"
LIST_URL = "https://arxiv.org/list/cs.AI/recent"

def main():
    s = requests.Session()
    r = s.get(LIST_URL, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.select('a[href^="/abs/"]')

    print(f"found {len(links)} abstract links (sample run)")

    for a in links[:5]:
        abs_url = BASE + a.get("href")
        print("GET", abs_url)
        time.sleep(15)   # robots.txt Crawl-delay 존중

if __name__ == "__main__":
    main()
