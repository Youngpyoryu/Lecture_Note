# 응답 스키마 유연 파싱
from typing import Any, Dict, List, Tuple


def parse_items_response(data: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], bool, str]:
    """
    다양한 API 응답 형태를 흡수해서 (items, has_next)를 표준 형태로 반환.
    return: (items, has_next, schema_tag)
    """

    # 1) 정상 케이스 후보 키들
    items = None
    for k in ("items", "results", "data", "rows"):
        v = data.get(k)
        if isinstance(v, list):
            items = v
            break

    # 2) has_next 후보 키들 (bool or 0/1)
    has_next = None
    for k in ("has_next", "hasNext", "next", "has_more", "hasMore"):
        v = data.get(k)
        if isinstance(v, bool):
            has_next = v
            break
        if v in (0, 1):
            has_next = bool(v)
            break

    # 3) next_page / next_url 형태
    if has_next is None:
        if data.get("next_page") is not None or data.get("nextPage") is not None:
            has_next = True
        elif isinstance(data.get("next"), str) and data.get("next"):
            has_next = True

    # 4) 최종 방어
    if items is None:
        # 에러 응답일 수도 있으므로, items는 빈 리스트로
        items = []

    if has_next is None:
        # has_next가 없다면: 보수적으로 False 처리 (루프 폭주 방지)
        has_next = False

    # 스키마 태그(디버깅용)
    schema_tag = "unknown"
    if "items" in data:
        schema_tag = "items/has_next"
    elif "results" in data:
        schema_tag = "results/*"
    elif "data" in data:
        schema_tag = "data/*"

    return items, has_next, schema_tag


def is_error_payload(data: Dict[str, Any]) -> bool:
    """
    items가 없는 대신 error, detail, message 등을 주는 경우를 감지.
    """
    for k in ("error", "errors", "detail", "message"):
        if k in data:
            return True
    return False
