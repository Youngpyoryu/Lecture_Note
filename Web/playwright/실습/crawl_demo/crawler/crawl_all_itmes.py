import requests

BASE = "http://127.0.0.1:8000"
EMAIL = "demo@demo.com"
PW = "pass1234"

def login(session):
    session.post(
        f"{BASE}/login",
        data={"email": EMAIL, "password": PW},
        allow_redirects=True,
    )

def main():
    s = requests.Session()
    login(s)

    page = 1
    while True:
        r = s.get(f"{BASE}/api/items", params={"page": page})
        data = r.json()

        print(f"page={page}, items={len(data['items'])}")

        if not data["has_next"]:
            break
        page += 1

if __name__ == "__main__":
    main()
