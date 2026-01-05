import json
import csv
import time
from pathlib import Path
from typing import Any, Dict, List

import requests

from http_client import request_with_retry
from throttle import sleep_between_requests
from response_parser import parse_items_response, is_error_payload
from schema import normalize_item

BASE = "http://127.0.0.1:8000"
EMAIL = "demo@demo.com"
PW = "pass1234"

OUT_JSON = Path("items.json")
OUT_CSV = Path("items.csv")
CHECKPOINT = Path("checkpoint.json")


def load_checkpoint() -> Dict[str, Any]:
    if CHECKPOINT.exists():
        return json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    return {"next_page": 1, "seen_ids": [], "items": []}


def save_checkpoint(next_page: int, seen_ids: List[int], items: List[Dict[str, Any]]) -> None:
    payload = {
        "next_page": next_page,
        "seen_ids": seen_ids,
        "items_count": len(items),
        "items": items,  # 데모용. 대용량이면 파일 저장만 권장
    }
    CHECKPOINT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_outputs(items: List[Dict[str, Any]]) -> None:
    OUT_JSON.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    fieldnames = sorted({k for it in items for k in it.keys()})
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(items)


def login(session: requests.Session) -> None:
    session.post(
        f"{BASE}/login",
        data={"email": EMAIL, "password": PW},
        allow_redirects=True,
        timeout=10,
    )


def fetch_page(session: requests.Session, page: int) -> Dict[str, Any]:
    resp = request_with_retry(session, "GET", f"{BASE}/api/items", params={"page": page})

    if resp.status_code == 401:
        login(session)
        resp = request_with_retry(session, "GET", f"{BASE}/api/items", params={"page": page})

    resp.raise_for_status()
    return resp.json()


def main() -> None:
    cp = load_checkpoint()
    page = int(cp.get("next_page", 1))
    seen_ids = set(cp.get("seen_ids", []))
    items: List[Dict[str, Any]] = cp.get("items", [])

    print(f"Resume page={page} items={len(items)} seen={len(seen_ids)}")

    s = requests.Session()
    login(s)

    while True:
        data = fetch_page(s, page)

        # 에러 payload 감지
        if is_error_payload(data):
            print(f"[WARN] error payload at page={page}: {data}")
            break

        # 유연 파싱(3️⃣ 핵심)
        page_items, has_next, schema_tag = parse_items_response(data)

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
            items.append(item)
            added += 1

        print(f"page={page} schema={schema_tag} fetched={len(page_items)} added={added} total={len(items)} has_next={has_next}")

        save_checkpoint(next_page=page + 1, seen_ids=sorted(seen_ids), items=items)

        sleep_between_requests(0.2, 0.6)

        if not has_next:
            break
        page += 1

    write_outputs(items)
    print("Done. items.json / items.csv saved. (delete checkpoint.json to start fresh)")


if __name__ == "__main__":
    main()
