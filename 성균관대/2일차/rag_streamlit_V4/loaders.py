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
    # - 하나의 “원본 문서” 단위(PDF page / URL / Notes)를 표현합니다.
    # - text는 원문, meta는 source/url/page 같은 “추적 정보”를 담습니다.
    # - chunking 단계에서 meta를 복사해 [source|p?|c?] 인용이 가능해집니다.
    text: str
    meta: Dict[str, Any]


def _clean_text(s: str) -> str:
    # - PDF/웹 텍스트의 불필요한 공백/개행을 최소 정제합니다.
    # - chunk 경계에서 생기는 잡음을 줄여 retrieval 품질을 안정화합니다.
    # - 실습용으로 과도한 정제보다 “일관성”을 우선합니다.
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def load_pdf_documents(file_bytes: bytes, source_name: str) -> List[Document]:
    # - PDF를 “페이지 단위 Document” 리스트로 로드합니다(meta에 page 포함).
    # - pypdf.PdfReader는 bytes가 아닌 seek 가능한 stream을 요구하므로 BytesIO로 감쌉니다.
    # - page meta가 있어야 RAG 답변에서 페이지 단위로 검증 가능한 citation이 됩니다.
    stream = io.BytesIO(file_bytes)
    reader = PdfReader(stream)

    docs: List[Document] = []
    for pageno, page in enumerate(reader.pages, start=1):
        t = page.extract_text() or ""
        t = _clean_text(t)
        if t:
            docs.append(Document(text=t, meta={"source": source_name, "page": pageno}))
    return docs


def load_web_document(url: str, timeout: float = 15.0) -> Document:
    # - URL HTML을 가져와 텍스트만 추출하는 단순 로더입니다.
    # - 실무에서는 본문 추출/보일러플레이트 제거가 중요하지만, 실습은 흐름 이해가 목적입니다.
    # - meta에 url을 넣어 evidence에서 출처를 추적할 수 있게 합니다.
    r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text("\n")
    text = _clean_text(text)
    return Document(text=text, meta={"url": url})


def load_notes_document(notes: str) -> Document:
    # - 사용자가 붙여넣은 메모를 “문서 1개”로 취급합니다.
    # - meta.source="notes"로 표시해 PDF/웹과 구분됩니다.
    # - 강의에서는 빠른 데이터 입력 채널(즉시 실험용) 역할을 합니다.
    return Document(text=_clean_text(notes), meta={"source": "notes"})


def split_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    # - 문자 기반 청킹(토큰 기반보다 단순)으로 실습에 적합합니다.
    # - overlap을 주어 chunk 경계에서 정보 손실을 줄입니다.
    # - chunk_size/overlap을 UI에서 바꿔가며 품질 변화를 관찰할 수 있습니다.
    text = _clean_text(text)
    if not text:
        return []
    step = max(1, chunk_size - overlap)
    out: List[str] = []
    for i in range(0, len(text), step):
        part = text[i: i + chunk_size].strip()
        if part:
            out.append(part)
    return out


def make_chunks(docs: List[Document], chunk_size: int, overlap: int) -> List[Dict[str, Any]]:
    # - Document 리스트를 {"text":..., "meta":...} chunk 리스트로 변환합니다.
    # - chunk_id를 전역 증가로 부여해 rerank/citation에서 안정적으로 추적합니다.
    # - meta는 복사하고 chunk_id만 추가해 “근거 단위” 식별을 가능하게 합니다.
    chunks: List[Dict[str, Any]] = []
    cid = 0
    for d in docs:
        parts = split_text(d.text, chunk_size=chunk_size, overlap=overlap)
        for p in parts:
            chunks.append({"text": p, "meta": {**d.meta, "chunk_id": cid}})
            cid += 1
    return chunks
