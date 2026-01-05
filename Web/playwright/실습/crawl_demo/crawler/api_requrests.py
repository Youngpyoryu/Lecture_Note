import requests

BASE = "http://127.0.0.1:8000"
EMAIL = "demo@demo.com"
PW = "pass1234"

s = requests.Session()

# 1) 로그인 (쿠키 세션 확보)
resp = s.post(f"{BASE}/login", data={"email": EMAIL, "password": PW}, allow_redirects=True)
print("Login status:", resp.status_code)

# 2) API 직접 호출
r = s.get(f"{BASE}/api/items", params={"page": 1})
print("API status:", r.status_code)
data = r.json()
print("items count:", len(data["items"]))
print("first item:", data["items"][0])
