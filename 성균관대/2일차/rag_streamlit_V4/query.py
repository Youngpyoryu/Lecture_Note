res = collection.query(
    query_texts=["질문: MMR이 뭐야?"],
    n_results=4,
    # where={"source": "a.pdf"}  # 메타 필터(예시)
)

# res["documents"][0], res["metadatas"][0], res["distances"][0] 등을 사용
print(res)

