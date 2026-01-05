import time
import random
from typing import Any, Dict, List

import requests

from http_client import request_with_retry
from throttle import sleep_between_requests
from response_parser import parse_items_response, is_error_payload
from schema import normalize_item


BASE = "http://127.0.0.1:8000"
EMAIL = "demo@demo.com"
PW = "pass1234"


def login(session: requests.Session) -> None:
    session.post(
        f"{BASE}/login",
        data={"email": EMAIL, "password": PW},
        allow_redirects=True,
    )


def fetch_page(session: requests.Session, page: int) -> Dict[str, Any]:
    resp = request_with_retry(session, "GET", f"{BASE}/api/items", params={"page": page})

    if resp.status_code == 401:
        login(session)
        resp = request_with_retry(session, "GET", f"{BASE}/api/items", params={"page": page})

    resp.raise_for_status()
    return resp.json()


def main() -> None:
    s = requests.Session()
    login(s)

    page = 1
    seen_ids = set()
    collected: List[Dict[str, Any]] = []

    while True:
        data = fetch_page(s, page)

        # 1) 에러 payload 감지(디버깅/로그 포인트)
        if is_error_payload(data):
            print(f"[WARN] page={page} error payload: {data}")
            # 보수적으로 중단(교안에서는 중단이 낫습니다)
            break

        # 2) 유연 파싱(핵심)
        page_items, has_next, schema_tag = parse_items_response(data)

        # 3) 최소 필드 기반 정규화 + 누락 방어
        added = 0
        for raw in page_items:
            if not isinstance(raw, dict):
                continue
            item = normalize_item(raw)
            if item is None:
                continue
            _id = item["id"]
            if _id in seen_ids:
                continue
            seen_ids.add(_id)
            collected.append(item)
            added += 1

        print(f"page={page} schema={schema_tag} fetched={len(page_items)} added={added} total={len(collected)} has_next={has_next}")

        # 4) 요청 간 sleep
        sleep_between_requests(0.2, 0.6)

        if not has_next:
            break
        page += 1

    print(f"Done. collected={len(collected)}")


if __name__ == "__main__":
    main()
