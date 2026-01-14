const form = document.getElementById("form");
const input = document.getElementById("content");
const list = document.getElementById("list");
const statusEl = document.getElementById("status");

/* =========================
 * (03단계) 목록 가져오기
 * - GET /api/todos
 * - 가져온 데이터를 render()로 화면에 그림
 * ========================= */
async function fetchTodos() {
  statusEl.textContent = "불러오는 중...";
  const res = await fetch("/api/todos");
  const todos = await res.json();
  render(todos);
  statusEl.textContent = `총 ${todos.length}개`;
}

/* ==========================================================
 *  (04단계에서 '추가된' 핵심: render()에 "삭제 버튼"을 붙임
 *
 * - 03단계: li에 content + 날짜만 표시
 * - 04단계: 각 li마다 [삭제] 버튼을 추가
 *   버튼 클릭 시:
 *     1) DELETE /api/todos/:id 요청
 *     2) 성공하면 fetchTodos()로 리스트를 다시 받아와 갱신
 * - 시각적 확인:
 *   - 버튼 누르면 목록에서 바로 사라짐
 * ========================================================== */
function render(todos) {
  list.innerHTML = "";
  for (const t of todos) {
    const li = document.createElement("li");

    // (03) 내용 표시
    const text = document.createElement("span");
    text.textContent = t.content;
    li.appendChild(text);

    // (03) 날짜 표시
    const meta = document.createElement("span");
    meta.className = "meta";
    meta.textContent = `(${new Date(t.createdAt).toLocaleString()})`;
    li.appendChild(meta);

    //  (04) 삭제 버튼 추가
    const delBtn = document.createElement("button");
    delBtn.textContent = "삭제";
    delBtn.style.marginLeft = "10px";

    delBtn.addEventListener("click", async () => {
      // (04) 서버 Delete API 호출
      const res = await fetch(`/api/todos/${t._id}`, { method: "DELETE" });

      // (04) 실패 처리(초심자용: 간단히 alert)
      if (!res.ok) {
        const err = await res.json();
        alert(err.message || "삭제 실패");
        return;
      }

      // (04) 삭제 후 리스트 다시 로드 → 화면 즉시 갱신
      await fetchTodos();
    });

    li.appendChild(delBtn);

    list.appendChild(li);
  }
}

/* =========================
 * (03단계) 폼 제출 -> 생성 API 호출
 * - POST /api/todos
 * - 성공하면 fetchTodos()로 즉시 갱신
 * ========================= */
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const content = input.value.trim();
  if (!content) return;

  const res = await fetch("/api/todos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });

  if (!res.ok) {
    const err = await res.json();
    alert(err.message || "에러");
    return;
  }

  input.value = "";
  await fetchTodos();
});

// (03) 첫 화면 로드시 목록 표시
fetchTodos();
