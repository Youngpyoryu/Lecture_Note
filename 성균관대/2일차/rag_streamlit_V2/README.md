## 실습 2: 메타데이터 기반 RAG로 업그레이드 (검증 가능한 RAG)

### 목표
- RAG의 핵심은 "답변 생성"이 아니라 "근거 기반 검증 가능성"이다.
- Chunk에 출처/페이지/URL 정보를 부여하고, Evidence에 함께 표시한다.
- Streamlit에서 인덱스의 정체성(문서/파라미터)을 명확히 표시해 재현성을 확보한다.

---

### 1) 1단계(기존) 문제점 복기
1. Chunk가 문자열(List[str])이라 출처/페이지/URL이 없어 근거 추적이 불가능
2. PDF를 한 덩어리 문자열로 합쳐 페이지 경계가 사라짐 → citation 불가
3. chunk_size/overlap을 바꿔도 인덱스 재생성 여부가 UI에서 모호
4. Chunk 미리보기가 첫 chunk 1개뿐이라 디버깅이 약함

---

### 2) 해결 전략(2단계)
- 문서 로딩 결과를 공통 포맷으로 통일:
  - pages = [{"text": "...", "meta": {...}}]
- 청킹 결과는:
  - chunks = [{"text": "chunk...", "meta": {..., "chunk_id": n}}]
- Evidence 출력 시 meta를 함께 표기:
  - [source|p3|c12] 형태로 citation 제공

---

### 3) 확인 과제
- PDF 업로드 후 Evidence expander 제목에 "source + page + chunk_id"가 나타나는지 확인
- chunk_size/overlap을 바꾼 뒤 인덱스를 재생성하지 않으면 설정 불일치가 생길 수 있음을 설명할 수 있는지 확인
- 적절한 top_k를 조절하며 근거 품질 변화를 관찰

---

### 다음 단계(실습 3 예고)
- Retrieval 품질 업그레이드:
  - Query rewrite → fetch_k 후보 확장 → MMR(중복 감소) → Re-rank(정확도 상승)
- 실무 확장:
  - FAISS 인덱스 저장/로드(persist)로 재실행 비용 절감
