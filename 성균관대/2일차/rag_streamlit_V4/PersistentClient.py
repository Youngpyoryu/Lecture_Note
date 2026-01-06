import chromadb
from chromadb.config import Settings

# allow_reset은 reset() 같은 파괴적 동작을 허용하는 옵션입니다(실습 시만 권장).
client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(allow_reset=True),
)

collection = client.get_or_create_collection(name="rag_chunks")
