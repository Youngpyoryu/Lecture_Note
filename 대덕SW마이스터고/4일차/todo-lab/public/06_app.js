const form = document.getElementById("form");
const input = document.getElementById("content");

const qInput = document.getElementById("q");
const clearBtn = document.getElementById("clear");

const list = document.getElementById("list");
const statusEl = document.getElementById("status");

// 현재 검색어 상태(브라우저에서 유지)
let currentQ = "";

async function fetchTodos() {
  statusEl.textContent = "불러오는 중...";

  //  (06) q가 있으면 쿼리스트링으로 붙여서 요청
  const url = currentQ ? `/api/todos?q=${encodeURIComponent(currentQ)}` : "/api/todos";

  const res = await fetch(url);
  const todos = await res.json();

  render(todos);
  statusEl.textContent = currentQ
    ? `검색어: "${currentQ}" | 결과 ${todos.length}개`
    : `총 ${todos.length}개`;
}

function render(todos) {
  list.innerHTML = "";
  for (const t of todos) {
    const li = document.createElement("li");

    // done 토글
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = !!t.done;
    checkbox.addEventListener("change", async () => {
      const res = await fetch(`/api/todos/${t._id}/toggle`, { method: "PATCH" });
      if (!res.ok) {
        const err = await res.json();
        alert(err.message || "토글 실패");
        return;
      }
      await fetchTodos();
    });
    li.appendChild(checkbox);

    // 텍스트(완료면 줄긋기)
    const text = document.createElement("span");
    text.textContent = " " + t.content;
    if (t.done) text.style.textDecoration = "line-through";
    li.appendChild(text);

    // 날짜
    const meta = document.createElement("span");
    meta.className = "meta";
    meta.textContent = `(${new Date(t.createdAt).toLocaleString()})`;
    li.appendChild(meta);

    // 삭제
    const delBtn = document.createElement("button");
    delBtn.textContent = "삭제";
    delBtn.style.marginLeft = "10px";
    delBtn.addEventListener("click", async () => {
      const res = await fetch(`/api/todos/${t._id}`, { method: "DELETE" });
      if (!res.ok) {
        const err = await res.json();
        alert(err.message || "삭제 실패");
        return;
      }
      await fetchTodos();
    });
    li.appendChild(delBtn);

    list.appendChild(li);
  }
}

// (추가)
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
    alert(err.message || "추가 실패");
    return;
  }

  input.value = "";
  await fetchTodos();
});

//  (06) 검색어 입력 시 즉시 검색(타이핑마다)
qInput.addEventListener("input", async () => {
  currentQ = qInput.value.trim();
  await fetchTodos();
});

//  (06) 초기화 버튼
clearBtn.addEventListener("click", async () => {
  qInput.value = "";
  currentQ = "";
  await fetchTodos();
});

// 첫 로드
fetchTodos();
