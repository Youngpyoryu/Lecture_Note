import requests
from bs4 import BeautifulSoup

url = "http://127.0.0.1:8000/"
html = requests.get(url).text
soup = BeautifulSoup(html, "html.parser")

items = soup.select("#items li")
print("HTML에서 찾은 아이템 개수:", len(items))
