from __future__ import annotations
from typing import List
import re

import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader


def load_pdf_text(file_bytes: bytes) -> str:
    """
    PDF 바이트를 받아 전체 텍스트를 추출해 하나의 문자열로 반환한다.

    Args:
        file_bytes: PDF 파일의 바이트(bytes). (Streamlit 업로더의 getvalue() 결과 등)

    Returns:
        PDF 전체 페이지에서 추출한 텍스트를 '\n'로 이어붙인 문자열.

    Notes:
        - PdfReader.pages를 순회하며 page.extract_text()로 텍스트를 추출한다.
        - extract_text()가 None을 반환할 수 있어 빈 문자열로 대체한다.
        - 페이지 구분은 '\n'로 합치며, 최종적으로 strip()으로 앞뒤 공백을 제거한다.
    """
    reader = PdfReader(file_bytes)
    texts = []
    for page in reader.pages:
        # 각 페이지의 텍스트 추출(없으면 빈 문자열)
        t = page.extract_text() or ""
        texts.append(t)
    return "\n".join(texts).strip()


def load_web_text(url: str, timeout: float = 15.0) -> str:
    """
    웹 페이지를 요청하여 본문 텍스트를 추출해 반환한다.

    Args:
        url: 크롤링할 웹 페이지 URL
        timeout: HTTP 요청 타임아웃(초)

    Returns:
        HTML에서 스크립트/스타일/네비게이션 등을 제거한 뒤 텍스트만 추출한 문자열.

    Notes:
        - httpx.get(..., follow_redirects=True)로 리다이렉트까지 따라간다.
        - raise_for_status()로 4xx/5xx 에러를 예외로 처리한다.
        - BeautifulSoup로 파싱 후 script/style/noscript/header/footer/nav 등은 제거한다.
        - soup.get_text(separator="\n")로 텍스트를 뽑고,
          연속된 줄바꿈을 정규식으로 정리하여 가독성을 높인다.
    """
    r = httpx.get(url, timeout=timeout, follow_redirects=True)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # 제거: 스크립트/스타일/네비 등(본문과 무관하거나 노이즈가 큰 영역)
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()

    # 텍스트 추출: 요소 사이를 줄바꿈으로 구분
    text = soup.get_text(separator="\n")

    # 2줄 이상 연속 줄바꿈을 2줄로 줄여 과도한 공백을 정리
    text = re.sub(r"\n{2,}", "\n\n", text).strip()
    return text


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    """
    긴 텍스트를 일정 길이(chunk_size)로 자르되, 문맥 단절을 줄이기 위해 overlap만큼 겹치게 분할한다.

    Args:
        text: 입력 원문 텍스트
        chunk_size: 청크 1개의 최대 문자 길이
        overlap: 다음 청크로 넘어갈 때 겹칠 문자 길이(문맥 보존용)

    Returns:
        분할된 청크 문자열 리스트. 입력이 비어있으면 [] 반환.

    Notes:
        - 먼저 모든 공백류(줄바꿈/탭/다중 공백)를 단일 스페이스로 정규화한다.
        - 슬라이딩 윈도우 방식:
            start에서 시작해 start+chunk_size까지 자르고,
            다음 start는 (end - overlap)로 이동한다.
        - overlap이 chunk_size 이상이면 start가 제대로 전진하지 않을 수 있으므로
          실제 사용 시 overlap < chunk_size를 권장한다.
    """
    # 공백 정리: 여러 공백/줄바꿈/탭 등을 단일 공백으로 통일
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])

        # 마지막까지 도달하면 종료
        if end == len(text):
            break

        # 다음 청크 시작 위치(겹침 적용)
        start = max(0, end - overlap)

    return chunks
