# loaders.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any
import io
import re

from pypdf import PdfReader
import requests
from bs4 import BeautifulSoup


@dataclass
class Document:
    # - 하나의 “원본 문서 단위”를 표현합니다(PDF 페이지 1개, URL 1개, Notes 1개).
    # - text에는 본문 텍스트를, meta에는 source/url/page 같은 추적 정보를 넣습니다.
    # - 이후 chunking에서 meta를 복사해 [source|p?|c?] 형태의 인용/근거 표기가 가능해집니다.
    text: str
    meta: Dict[str, Any]


def _clean_text(s: str) -> str:
    # - PDF/웹 텍스트의 불필요한 공백/개행을 최소 정리합니다(실습 안정성).
    # - 완벽한 전처리보다 “chunk가 지나치게 깨지지 않게” 하는 목적입니다.
    # - 동일 문서라도 청킹 결과가 일관되게 나오도록 기본 정규화만 수행합니다.
    s = (s or "").replace("\u00a0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def load_pdf_documents(file_bytes: bytes, source_name: str) -> List[Document]:
    # - pypdf.PdfReader는 seek() 가능한 파일 객체를 기대하므로 bytes는 BytesIO로 감쌉니다.
    # - PDF를 페이지 단위로 쪼개 meta.page를 부여하면 citation이 정확해집니다.
    # - 페이지 단위 chunking이 가능해져 retrieval 다양성과 디버깅 품질도 좋아집니다.
    reader = PdfReader(io.BytesIO(file_bytes))
    docs: List[Document] = []
    for pageno, page in enumerate(reader.pages, start=1):
        t = _clean_text(page.extract_text() or "")
        if t:
            docs.append(Document(text=t, meta={"source": source_name, "page": pageno}))
    return docs


def load_web_document(url: str, timeout: float = 15.0) -> Document:
    # - URL의 HTML을 가져와 텍스트를 추출하는 “간단 버전”입니다.
    # - 실무는 본문만 추출(selector/boilerplate 제거)이 중요하지만 실습은 흐름이 목적입니다.
    # - meta.url을 저장해 답변에서 출처 추적이 가능하도록 합니다.
    r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    text = _clean_text(soup.get_text("\n"))
    return Document(text=text, meta={"url": url})


def load_notes_document(notes: str) -> Document:
    # - 사용자가 붙여넣는 Notes를 하나의 문서로 취급합니다.
    # - meta.source="notes"로 PDF/웹과 구분되도록 합니다.
    # - 강의에서는 Notes가 “가장 빠른 데이터 입력 채널” 역할을 합니다.
    return Document(text=_clean_text(notes), meta={"source": "notes"})


def split_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    # - 문자 기반 청킹(실습용)입니다: 토큰 기반보다 단순하고 디버깅이 쉽습니다.
    # - overlap으로 경계 정보 손실을 줄여 retrieval 안정성을 높입니다.
    # - chunk_size/overlap은 문서 성격에 따라 달라지므로 슬라이더로 실험하게 합니다.
    text = _clean_text(text)
    if not text:
        return []
    step = max(1, chunk_size - overlap)
    out: List[str] = []
    for i in range(0, len(text), step):
        part = text[i : i + chunk_size].strip()
        if part:
            out.append(part)
    return out


def make_chunks(docs: List[Document], chunk_size: int, overlap: int) -> List[Dict[str, Any]]:
    # - Document 리스트를 {"text":..., "meta":...} chunk 리스트로 변환합니다.
    # - chunk_id를 전역 증가로 부여해 retrieval/rerank/citation에서 안정적으로 추적합니다.
    # - meta는 원문 추적용 정보(source/url/page)를 유지하고 chunk_id만 추가합니다.
    chunks: List[Dict[str, Any]] = []
    cid = 0
    for d in docs:
        parts = split_text(d.text, chunk_size=chunk_size, overlap=overlap)
        for p in parts:
            chunks.append({"text": p, "meta": {**d.meta, "chunk_id": cid}})
            cid += 1
    return chunks
