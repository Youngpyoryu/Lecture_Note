# 메타데이터 포함("페이지 리스트"+ Chunking)
## PDF: 페이지별로 text+meta(source,page) 생성
## Web: text+meta(url)
## Notes: text+meta(source="notes")
## chunk_pages(): chunk_id를 부여하여 디버깅/인용에 활용
from __future__ import annotations
from typing import List, Dict, Any, Union
import re

import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader


def _clean_text(text: str) -> str:
    """
    텍스트 정리 유틸 함수.

    목적:
    - PDF/웹/노트에서 가져온 텍스트에는 제어문자(널 문자)나 과도한 공백/줄바꿈이 섞이기 쉬움
    - 너무 공격적으로 한 줄로 합치면 문서 구조(문단/섹션)가 망가질 수 있어 "완만하게" 정리

    처리 내용:
    1) 널 문자(\x00) 제거(공백으로 치환)
    2) 연속된 공백/탭을 1칸 공백으로 축소
    3) 3줄 이상 연속 줄바꿈은 2줄로 축소(너무 큰 공백 제거)
    4) 앞뒤 공백 제거
    """
    # 공백 정리: 너무 공격적으로 한 줄로 만들면 문서 구조가 망가질 수 있어 완만하게 정리
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_pdf_pages(file_obj) -> List[Dict[str, Any]]:
    """
    PDF를 페이지 단위로 텍스트를 추출해 리스트로 반환한다.

    Args:
        file_obj:
            Streamlit 업로더 객체 또는 파일 핸들.
            PdfReader가 읽을 수 있는 객체여야 한다.

    Returns:
        페이지 리스트:
        [
          {"text": "...", "meta": {"source": "file.pdf", "page": 1}},
          {"text": "...", "meta": {"source": "file.pdf", "page": 2}},
          ...
        ]

    Notes:
        - page 번호는 사람이 보기 좋게 1부터 시작한다.
        - 페이지 텍스트가 비어 있으면 해당 페이지는 건너뛴다(노이즈 제거).
        - meta.source는 업로드 파일명(file_obj.name)이 있으면 그것을 사용한다.
    """
    reader = PdfReader(file_obj)

    # 파일명이 있으면 사용, 없으면 기본값 사용
    source = getattr(file_obj, "name", "uploaded.pdf")

    pages: List[Dict[str, Any]] = []
    for i, page in enumerate(reader.pages, start=1):
        # 페이지 텍스트 추출(없을 수 있으므로 빈 문자열로 대체)
        t = page.extract_text() or ""

        # 텍스트 정리(널 문자, 과도한 공백/줄바꿈 등)
        t = _clean_text(t)

        # 텍스트가 비면 스킵(예: 이미지-only 페이지 등)
        if not t:
            continue

        # 페이지 단위 결과로 저장
        pages.append({"text": t, "meta": {"source": source, "page": i}})

    return pages


def load_web_pages(url: str, timeout: float = 15.0) -> List[Dict[str, Any]]:
    """
    웹 페이지를 불러와 텍스트를 추출한 뒤, 단일 "페이지"로 감싸 반환한다.

    Args:
        url: 크롤링할 URL
        timeout: http 요청 타임아웃(초)

    Returns:
        웹 페이지 리스트(보통 1개 원소):
        [
          {"text": "...", "meta": {"url": "<url>"}}
        ]
        텍스트가 비어있으면 [] 반환

    Notes:
        - follow_redirects=True로 리다이렉트 허용
        - script/style/nav 등 본문과 무관하거나 노이즈가 큰 태그는 제거
        - 결과를 페이지 분할하지 않고 "한 페이지"로 취급
          (추가로 섹션 단위 분할을 하고 싶다면 여기서 로직을 확장 가능)
    """
    r = httpx.get(url, timeout=timeout, follow_redirects=True)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # 본문 텍스트에 방해가 되는 요소 제거
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()

    # 텍스트만 추출
    text = soup.get_text(separator="\n")
    text = _clean_text(text)

    return [{"text": text, "meta": {"url": url}}] if text else []


def load_notes_pages(text: str) -> List[Dict[str, Any]]:
    """
    사용자가 입력한 노트/메모 텍스트를 '페이지 1개'로 감싸 반환한다.

    Args:
        text: 사용자 입력 메모

    Returns:
        [
          {"text": "...", "meta": {"source": "notes"}}
        ]
        텍스트가 비어있으면 [] 반환
    """
    text = _clean_text(text or "")
    return [{"text": text, "meta": {"source": "notes"}}] if text else []


def chunk_pages(
    pages: List[Dict[str, Any]],
    chunk_size: int = 800,
    overlap: int = 120
) -> List[Dict[str, Any]]:
    """
    페이지 리스트를 받아 chunk 단위로 쪼갠 뒤, chunk 리스트를 반환한다.

    Args:
        pages:
            load_pdf_pages/load_web_pages/load_notes_pages가 반환한 형태의 리스트
            예: [{"text": "...", "meta": {...}}, ...]
        chunk_size:
            한 chunk의 최대 문자 길이(문자 기반)
        overlap:
            다음 chunk로 넘어갈 때 겹칠 문자 수(문맥 연결을 위해 사용)

    Returns:
        chunk 리스트:
        [
          {"text": "chunk...", "meta": {..., "chunk_id": 0}},
          {"text": "chunk...", "meta": {..., "chunk_id": 1}},
          ...
        ]

    동작 방식(중요):
        - 각 page의 text를 공백 정규화(re.sub(r"\s+", " ", ...))로 한 줄 기반으로 만든 뒤,
          슬라이딩 윈도우로 chunk를 만든다.
        - meta는 페이지의 meta를 복사해서 chunk_id를 추가한다.
        - chunk_id는 전체 문서(모든 페이지) 기준으로 0부터 증가하며 유일하게 유지된다.

    주의:
        - overlap >= chunk_size이면 start가 충분히 전진하지 못해 무한 루프 위험이 커진다.
          일반적으로 overlap < chunk_size를 권장한다.
        - 현재는 문장 경계/단락 경계를 고려하지 않는 "문자 길이 기준" 청킹이다.
          (문장 단위/토큰 단위 청킹으로 개선 가능)
    """
    chunks: List[Dict[str, Any]] = []
    chunk_id = 0

    for p in pages:
        # 페이지 텍스트를 공백 정규화해서 한 줄에 가깝게 만든 뒤 청킹
        text = re.sub(r"\s+", " ", (p.get("text") or "")).strip()
        if not text:
            continue

        # 페이지 메타 복사(원본을 수정하지 않기 위해 dict()로 복제)
        meta_base = dict(p.get("meta", {}))

        start = 0
        while start < len(text):
            end = min(len(text), start + chunk_size)
            piece = text[start:end].strip()

            # chunk용 meta 구성: 페이지 메타 + chunk_id
            meta = dict(meta_base)
            meta["chunk_id"] = chunk_id

            # chunk 저장
            chunks.append({"text": piece, "meta": meta})
            chunk_id += 1

            # 마지막 chunk면 종료
            if end == len(text):
                break

            # overlap만큼 겹치도록 다음 시작 위치 설정
            start = max(0, end - overlap)

    return chunks

