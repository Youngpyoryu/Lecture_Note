# 예시: 당신의 chunks 구조를 Chroma 형태로 넣기
chunks = [
    {"text": "chunk text ...", "meta": {"source": "a.pdf", "page": 3, "chunk_id": 12}},
    {"text": "another chunk ...", "meta": {"source": "a.pdf", "page": 4, "chunk_id": 13}},
]

ids = [f"{c['meta'].get('source','src')}|p{c['meta'].get('page','')}|c{c['meta'].get('chunk_id','')}" for c in chunks]
documents = [c["text"] for c in chunks]
metadatas = [c["meta"] for c in chunks]

collection.add(
    ids=ids,
    documents=documents,
    metadatas=metadatas,
    # embeddings=...  # (선택) 직접 임베딩을 넣는 방식도 가능
)
