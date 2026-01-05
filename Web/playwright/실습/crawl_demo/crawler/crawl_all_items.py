import json
import csv
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

BASE = "http://127.0.0.1:8000"
EMAIL = "demo@demo.com"
PW = "pass1234"

OUT_JSON = Path("items.json")
OUT_CSV = Path("items.csv")
CHECKPOINT = Path("checkpoint.json")

API_PATH = "/api/items"
LOGIN_PATH = "/login"

TIMEOUT_SEC = 10
MAX_RETRIES = 5
BASE_BACKOFF_SEC = 0.6  # 0.6, 1.2, 2.4, 4.8, ...
THROTTLE_SEC = 0.2      # 요청 간 최소 쉬는 시간(과부하 방지)


def load_checkpoint() -> Dict[str, Any]:
    if CHECKPOINT.exists():
        return json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    return {"next_page": 1, "seen_ids": [], "items": []}


def save_checkpoint(next_page: int, seen_ids: List[int], items: List[Dict[str, Any]]) -> None:
    payload = {
        "next_page": next_page,
        "seen_ids": seen_ids,
        "items_count": len(items),
        "items": items,  # 데모라 저장. 실무에선 용량 커지면 items는 파일로만 저장 권장
    }
    CHECKPOINT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def request_with_retry(session: requests.Session, method: str, url: str, **kwargs) -> requests.Response:
    last_err: Optional[Exception] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.request(method, url, timeout=TIMEOUT_SEC, **kwargs)
            # 5xx는 재시도
            if 500 <= resp.status_code < 600:
                raise requests.HTTPError(f"Server error {resp.status_code}", response=resp)
            return resp
        except Exception as e:
            last_err = e
            sleep_s = BASE_BACKOFF_SEC * (2 ** (attempt - 1))
            print(f"[retry {attempt}/{MAX_RETRIES}] {method} {url} failed: {e} -> sleep {sleep_s:.1f}s")
            time.sleep(sleep_s)
    raise last_err  # type: ignore[misc]


def login(session: requests.Session) -> None:
    url = f"{BASE}{LOGIN_PATH}"
    resp = request_with_retry(
        session,
        "POST",
        url,
        data={"email": EMAIL, "password": PW},
        allow_redirects=True,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Login failed: status={resp.status_code}")
    # 로그인 후 세션 쿠키가 session에 저장됨


def fetch_page(session: requests.Session, page: int) -> Dict[str, Any]:
    url = f"{BASE}{API_PATH}"
    resp = request_with_retry(session, "GET", url, params={"page": page})
    if resp.status_code == 401:
        raise RuntimeError("Unauthorized (401). Login/session failed.")
    resp.raise_for_status()
    return resp.json()


def write_outputs(items: List[Dict[str, Any]]) -> None:
    # JSON
    OUT_JSON.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    # CSV (키가 달라도 안전하게: 전체 키 union)
    fieldnames = sorted({k for it in items for k in it.keys()})
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(items)


def main() -> None:
    cp = load_checkpoint()
    next_page = int(cp.get("next_page", 1))
    seen_ids = set(cp.get("seen_ids", []))
    items: List[Dict[str, Any]] = cp.get("items", [])

    print(f"Resume from page={next_page}, already_items={len(items)}, seen_ids={len(seen_ids)}")

    s = requests.Session()
    login(s)

    page = next_page
    while True:
        data = fetch_page(s, page)
        page_items = data.get("items", [])
        has_next = bool(data.get("has_next", False))

        added = 0
        for it in page_items:
            # 중복 제거 기준: id
            _id = it.get("id")
            if _id is None:
                continue
            if _id in seen_ids:
                continue
            seen_ids.add(_id)
            items.append(it)
            added += 1

        print(f"page={page} fetched={len(page_items)} added={added} total={len(items)} has_next={has_next}")

        # 체크포인트 저장: 다음 page부터 이어서
        save_checkpoint(next_page=page + 1, seen_ids=sorted(seen_ids), items=items)

        # 요청 간 휴식(예의 + 안정성)
        time.sleep(THROTTLE_SEC)

        if not has_next:
            break
        page += 1

    # 최종 산출물 저장
    write_outputs(items)

    print(f"Done. Saved: {OUT_JSON.resolve()} and {OUT_CSV.resolve()}")
    print(f"Checkpoint: {CHECKPOINT.resolve()} (delete it to start fresh)")


if __name__ == "__main__":
    main()
