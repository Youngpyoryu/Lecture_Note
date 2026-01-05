import requests

BASE = "http://127.0.0.1:8000"
EMAIL = "demo@demo.com"
PW = "pass1234"

s = requests.Session()
s.post(f"{BASE}/login", data={"email": EMAIL, "password": PW}, allow_redirects=True)

all_items = []
page = 1
while True:
    r = s.get(f"{BASE}/api/items", params={"page": page})
    r.raise_for_status()
    data = r.json()
    all_items.extend(data["items"])
    if not data["has_next"]:
        break
    page += 1

print("TOTAL:", len(all_items))
print("LAST:", all_items[-1])
print("ALL ITEMS:", all_items)