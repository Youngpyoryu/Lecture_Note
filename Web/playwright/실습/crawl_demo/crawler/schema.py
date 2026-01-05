# 최소 필드 기준 저장(방어적 정규화)

from typing import Any, Dict, Optional


MIN_FIELDS = ("id",)  # 최소 기준: id는 있어야 중복제거 가능


def normalize_item(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    - 필드 누락/추가에 유연
    - 최소 필드(id)가 없으면 버림(None)
    - 필요한 최소 형태로 정리(교안에서는 raw를 그대로 저장해도 됨)
    """
    _id = raw.get("id")
    if _id is None:
        return None

    # 교안용: 일단 raw 전체를 저장하되, 자주 쓰는 키만 상단에 보이게 정리
    out: Dict[str, Any] = {"id": _id}

    # 선택 필드들(없어도 됨)
    for k in ("name", "title", "price", "amount", "created_at"):
        if k in raw:
            out[k] = raw.get(k)

    # 원본도 보관(원하면 제거 가능)
    out["_raw"] = raw
    return out
