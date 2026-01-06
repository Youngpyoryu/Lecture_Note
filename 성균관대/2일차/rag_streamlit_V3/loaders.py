# loaders.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any
import re
import io

from pypdf import PdfReader
import requests
from bs4 import BeautifulSoup


@dataclass
class Document:
    """
    하나의 '원본 문서' 단위를 표현하는 데이터 구조.

    사용 의도:
    - PDF: 페이지별로 Document를 여러 개 생성(각 Document에 page 메타 포함)
    - Web: URL 하나를 Document 1개로 생성(meta에 url 포함)
    - Notes: 사용자가 입력한 텍스트를 Document 1개로 생성(meta에 source="notes")

    Fields:
        text:
            문서의 본문 텍스트(페이지 텍스트, 웹 페이지 텍스트, 노트 텍스트 등)
        meta:
            출처 추적을 위한 메타데이터
            예) {"source": "file.pdf", "page": 3}, {"url": "https://..."} 등

    Notes:
        - 이후 make_chunks에서 meta를 복사 + chunk_id 추가로 근거 단위를 추적 가능하게 만든다.
        - answer 단계에서 [source|p?|c?] 형태 인용을 만들기 위한 기반이다.
    """
    # - 하나의 “원본 문서”를 표현합니다(PDF 1개, URL 1개, Notes 1개).
    # - text는 원문(또는 페이지별 원문)의 모음이고 meta에는 source/url/page 같은 추적 정보를 둡니다.
    # - 이후 chunking 단계에서 meta를 그대로 복사해 [source|p?|c?] 인용을 만들 수 있게 합니다.
    text: str
    meta: Dict[str, Any]


def _clean_text(s: str) -> str:
    """
    텍스트 정리(최소한의 전처리) 함수.

    목적:
    - PDF/웹에서 추출된 텍스트는 공백/개행이 과도하거나 불규칙한 경우가 많다.
    - 너무 공격적인 정제(전부 한 줄로 만들기 등)는 문서 구조를 망가뜨릴 수 있어,
      실습/데모에서 안정적인 수준으로만 정리한다.

    처리 내용:
    1) NBSP(\u00a0)를 일반 공백으로 치환
    2) 연속된 공백/탭을 1칸 공백으로 축소
    3) 3줄 이상 연속 개행을 2줄로 축소(과도한 빈 줄 제거)
    4) 앞뒤 공백 제거

    Args:
        s: 원본 텍스트

    Returns:
        정리된 텍스트
    """
    # - PDF/웹에서 나온 텍스트는 공백/개행이 지저분한 경우가 많습니다.
    # - 연속 공백/개행을 정리해서 chunk 품질(문장 단절, 불필요한 중복)을 개선합니다.
    # - “완벽한 정제”보다 실습용으로 안정적인 최소 정제를 목표로 합니다.
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def load_pdf_documents(file_bytes: bytes, source_name: str) -> List[Document]:
    """
    PDF 바이트를 읽어 '페이지 단위 Document 리스트'로 변환한다.

    Args:
        file_bytes:
            PDF 파일의 바이트.
            (Streamlit file_uploader의 getvalue() 결과를 그대로 넣는 형태를 기대)
        source_name:
            출처 표시용 이름(보통 업로드 파일명). meta["source"]로 저장됨.

    Returns:
        List[Document]:
            각 원소가 PDF의 한 페이지를 나타내는 Document 리스트.
            meta에는 {"source": source_name, "page": pageno}가 포함된다.

    Notes:
        - PdfReader는 내부적으로 seek 가능한 스트림을 요구하므로 BytesIO로 감싸준다.
        - extract_text()가 빈 문자열/None일 수 있어 방어 처리한다.
        - 텍스트가 비는 페이지(이미지 기반 등)는 건너뛴다.
    """
    # - PDF를 “페이지 단위 Document” 리스트로 로드합니다(메타에 page 포함).
    # - PdfReader는 bytes가 아니라 seek 가능한 stream을 요구하므로 BytesIO로 감쌉니다.
    # - 페이지 meta가 있으면 RAG 답변에서 [source|p3|c12]처럼 추적이 정확해집니다.
    stream = io.BytesIO(file_bytes)
    reader = PdfReader(stream)

    docs: List[Document] = []
    for pageno, page in enumerate(reader.pages, start=1):
        # 페이지 텍스트 추출(없으면 빈 문자열)
        t = page.extract_text() or ""
        t = _clean_text(t)

        # 텍스트가 존재하는 페이지만 Document로 생성
        if t:
            docs.append(Document(text=t, meta={"source": source_name, "page": pageno}))

    return docs


def load_web_document(url: str, timeout: float = 15.0) -> Document:
    """
    웹 페이지(URL)에서 텍스트를 추출해 Document 1개로 반환한다.

    Args:
        url: 대상 웹 페이지 URL
        timeout: 요청 타임아웃(초)

    Returns:
        Document:
            text: HTML에서 추출한 텍스트
            meta: {"url": url}

    Notes:
        - requests를 사용하여 HTML을 다운로드한다.
        - User-Agent를 넣어 일부 사이트에서 차단되는 확률을 줄인다.
        - 여기서는 본문 추출을 정교하게 하지 않고 soup.get_text로 단순 추출한다.
          (실무에서는 boilerplate 제거/본문 selector 사용 등이 중요할 수 있음)
    """
    # - URL의 HTML을 가져와 텍스트만 추출합니다(간단 버전).
    # - 실무에서는 본문 selector/boilerplate 제거가 중요하지만, 실습은 흐름 이해가 목적입니다.
    # - meta에 url을 넣어 citation에 출처를 남길 수 있게 합니다.
    r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # 단순 텍스트 추출(태그 구분을 줄바꿈으로)
    text = soup.get_text("\n")
    text = _clean_text(text)

    return Document(text=text, meta={"url": url})


def load_notes_document(notes: str) -> Document:
    """
    사용자가 입력한 노트/메모 텍스트를 Document 1개로 래핑한다.

    Args:
        notes: 사용자 입력 문자열

    Returns:
        Document:
            text: 정리된 노트 텍스트
            meta: {"source": "notes"}

    Notes:
        - PDF/웹과 구분하기 위해 meta에 source="notes"를 넣는다.
    """
    # - 사용자가 직접 붙여넣는 메모를 하나의 문서로 취급합니다.
    # - meta.source="notes"로 표시해 PDF/웹과 구분되도록 합니다.
    # - 강의에서는 Notes가 “빠른 데이터 입력 채널” 역할을 합니다.
    return Document(text=_clean_text(notes), meta={"source": "notes"})


def split_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    텍스트를 문자 기반 슬라이딩 윈도우로 chunk 리스트로 분할한다.

    Args:
        text: 입력 텍스트
        chunk_size: chunk 하나의 최대 문자 길이
        overlap: 인접 chunk 사이에 겹칠 문자 길이

    Returns:
        List[str]: chunk 문자열 리스트

    동작:
        - 먼저 _clean_text로 최소 정리
        - step = chunk_size - overlap
        - i를 0, step, 2*step ...으로 이동하며 text[i:i+chunk_size]를 추출

    Notes:
        - overlap이 chunk_size 이상이면 step이 0 이하가 될 수 있으므로 max(1, ...)로 방어.
        - 문장 경계/토큰 경계를 고려하지 않는 단순 방식이지만, 실습에서 이해가 쉽다.
    """
    # - 단순 문자 기반 chunking입니다(토큰 기반보다 쉽고 실습에 적합).
    # - overlap을 두어 경계에서 정보 손실을 줄이고 retrieval 안정성을 높입니다.
    # - 문서/언어에 따라 최적 chunk_size는 다르므로 슬라이더로 실험하게 합니다.
    text = _clean_text(text)
    if not text:
        return []

    # 다음 chunk 시작 간격(step). overlap이 크면 step이 작아지고 chunk가 많아진다.
    step = max(1, chunk_size - overlap)

    out: List[str] = []
    for i in range(0, len(text), step):
        part = text[i: i + chunk_size].strip()
        if part:
            out.append(part)

    return out


def make_chunks(docs: List[Document], chunk_size: int, overlap: int) -> List[Dict[str, Any]]:
    """
    Document 리스트를 받아 chunk(dict{text/meta}) 리스트로 변환한다.

    Args:
        docs: Document 리스트(PDF 페이지들, URL 문서, notes 문서 등)
        chunk_size: chunk 최대 문자 길이
        overlap: 인접 chunk 간 겹칠 길이

    Returns:
        List[Dict[str, Any]]:
            각 원소는 다음 형태를 가진다.
            {
              "text": "<chunk text>",
              "meta": { ...원본 meta..., "chunk_id": <global increasing id> }
            }

    설계 포인트:
        - chunk_id를 전역 증가로 부여하여 모든 chunk를 유일하게 식별
        - 원본 Document의 meta를 그대로 복사하고 chunk_id만 추가
          -> retrieval 결과를 UI에서 추적하고, 답변에서 인용([source|p?|c?])을 만들기 쉬움
    """
    # - Document 리스트를 입력받아 {"text":..., "meta":...} chunk 리스트로 변환합니다.
    # - chunk_id를 전역 증가로 부여해 rerank/citation에서 안정적으로 추적하게 합니다.
    # - meta는 그대로 복사하되 chunk_id만 추가해 “근거 단위”를 식별 가능하게 합니다.
    chunks: List[Dict[str, Any]] = []
    cid = 0

    for d in docs:
        # 문서(페이지/웹/노트) 텍스트를 chunk 문자열 리스트로 분할
        parts = split_text(d.text, chunk_size=chunk_size, overlap=overlap)

        for p in parts:
            # 원본 meta 복사 + chunk_id 추가
            chunks.append({"text": p, "meta": {**d.meta, "chunk_id": cid}})
            cid += 1

    return chunks
