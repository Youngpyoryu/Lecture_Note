# loaders.py
### 의도: 서로 다른 입력(PDF/Web/Notes)을 공통 포맷(pages)으로 통일하고, 이후 검색을 위한 chunks(meta 포함)를 생성한다.
### 핵심: PDF는 페이지 단위로 텍스트를 추출하고 source/page 메타를 붙이며, Web은 url, Notes는 source=notes로 메타를 붙인다.
### 청킹: chunk_pages()가 chunk_size/overlap 규칙으로 텍스트를 잘라 chunk_id를 부여한다.
### 효과: evidence가 어디서 왔는지 추적 가능해지고, RAG의 검증 가능성이 올라간다.

from __future__ import annotations

# 타입 힌트(가독성/정적 분석용)
from typing import List, Dict, Any
import re

# 웹 로딩(HTTP 요청)
import httpx
# HTML 파싱(본문 텍스트 추출)
from bs4 import BeautifulSoup
# PDF 텍스트 추출
from pypdf import PdfReader


def _clean_text(text: str) -> str:
    """
    텍스트 정제 유틸.
    - PDF/웹/노트에서 공통으로 발생하는 잡음을 줄이고,
      검색/청킹 안정성을 높이기 위한 전처리.
    """
    # PDF에서 종종 등장하는 NULL 문자 제거
    text = text.replace("\x00", " ")

    # 연속 공백/탭을 단일 공백으로 축약
    text = re.sub(r"[ \t]+", " ", text)

    # 과도한 줄바꿈(3개 이상)을 2개로 축약
    # (단락 구분은 유지하되 빈 줄 폭주를 방지)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 앞뒤 공백 제거
    return text.strip()


def load_pdf_pages(file_obj) -> List[Dict[str, Any]]:
    """
    PDF 파일 객체(Streamlit uploader 등)에서 페이지별 텍스트를 추출해 반환.
    반환 형식:
      [
        {"text": <page_text>, "meta": {"source": <filename>, "page": <page_number>}},
        ...
      ]
    """
    # pypdf로 PDF 열기
    reader = PdfReader(file_obj)

    # 업로드 파일명이 있으면 meta에 기록(없으면 기본값)
    source = getattr(file_obj, "name", "uploaded.pdf")

    pages: List[Dict[str, Any]] = []
    # 페이지 번호를 1부터 시작(사람이 보는 페이지 번호와 일치)
    for i, page in enumerate(reader.pages, start=1):
        # 페이지 텍스트 추출(추출 실패 시 None일 수 있어 빈 문자열 처리)
        t = page.extract_text() or ""

        # 공통 정제 적용
        t = _clean_text(t)

        # 빈 페이지 텍스트는 제외(불필요한 chunk/노이즈 방지)
        if t:
            pages.append({"text": t, "meta": {"source": source, "page": i}})

    return pages


def load_web_pages(url: str, timeout: float = 15.0) -> List[Dict[str, Any]]:
    """
    URL에서 HTML을 가져와 본문 텍스트를 추출해 반환.
    반환은 pages와 동일한 구조이지만 보통 웹은 1개 페이지로 반환:
      [{"text": <all_text>, "meta": {"url": <url>}}]
    """
    # follow_redirects=True: 리다이렉트(301/302) 대응
    r = httpx.get(url, timeout=timeout, follow_redirects=True)
    # 4xx/5xx면 예외 발생시켜 상위(UI)에서 표시하게 함
    r.raise_for_status()

    # HTML 파싱
    soup = BeautifulSoup(r.text, "html.parser")

    # 검색에 불필요하고 노이즈가 큰 영역 제거
    # (스크립트/스타일/네비게이션/헤더/푸터 등)
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()

    # 페이지 전체의 텍스트를 줄바꿈 기준으로 수집
    text = soup.get_text(separator="\n")

    # 공통 정제 적용
    text = _clean_text(text)

    # 텍스트가 비어있으면 빈 리스트(입력 없음 처리)
    return [{"text": text, "meta": {"url": url}}] if text else []


def load_notes_pages(text: str) -> List[Dict[str, Any]]:
    """
    사용자가 직접 입력한 노트/메모 텍스트를 pages 구조로 래핑.
    - notes는 페이지 개념이 없으므로 meta에 source="notes"만 부여.
    """
    # None 대비 및 공통 정제
    text = _clean_text(text or "")
    return [{"text": text, "meta": {"source": "notes"}}] if text else []


def chunk_pages(
    pages: List[Dict[str, Any]],
    chunk_size: int = 800,
    overlap: int = 120
) -> List[Dict[str, Any]]:
    """
    pages(list of {"text","meta"})를 chunk 단위로 분할.
    - chunk_size: chunk 텍스트 길이(문자 기준)
    - overlap: 다음 chunk로 넘어갈 때 이전 chunk의 끝 일부를 겹쳐서 가져옴
               (문맥 단절을 줄여 retrieval 성능을 높이기 위함)

    반환 형식:
      [
        {"text": <chunk_text>, "meta": {<page_meta> + "chunk_id": <int>}},
        ...
      ]
    """
    chunks: List[Dict[str, Any]] = []
    chunk_id = 0  # 전체 chunk에 대해 유일한 id를 부여(출처 표시에 사용)

    for p in pages:
        # 페이지 텍스트를 한 줄 공백 단위로 정규화(청킹 안정성 ↑)
        text = re.sub(r"\s+", " ", (p.get("text") or "")).strip()
        if not text:
            continue

        # 원본 meta를 복사해 chunk마다 공통으로 적용
        # (source/page/url 등)
        meta_base = dict(p.get("meta", {}))

        start = 0
        # 슬라이딩 윈도우 방식으로 chunk 생성
        while start < len(text):
            # chunk 끝 인덱스(문자 단위)
            end = min(len(text), start + chunk_size)

            # 해당 구간 텍스트 조각
            piece = text[start:end].strip()

            # chunk별 meta 구성
            meta = dict(meta_base)
            meta["chunk_id"] = chunk_id

            # chunk 저장
            chunks.append({"text": piece, "meta": meta})
            chunk_id += 1

            # 끝까지 왔다면 종료
            if end == len(text):
                break

            # 다음 시작점: overlap만큼 되돌려서 이어붙이기
            # 예) end=800, overlap=120 -> start=680
            start = max(0, end - overlap)

    return chunks






