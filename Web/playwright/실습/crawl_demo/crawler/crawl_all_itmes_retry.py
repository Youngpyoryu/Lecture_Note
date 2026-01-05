import requests
from http_client import request_with_retry
from throttle import sleep_between_requests

BASE = "http://127.0.0.1:8000"

def main():
    s = requests.Session()

    # login 생략(기존 코드 재사용 가능)

    page = 1
    while True:
        resp = request_with_retry(
            s,
            "GET",
            f"{BASE}/api/items",
            params={"page": page},
        )

        data = resp.json()
        print(f"page={page}, items={len(data['items'])}")

        sleep_between_requests()

        if not data.get("has_next"):
            break
        page += 1

if __name__ == "__main__":
    main()

