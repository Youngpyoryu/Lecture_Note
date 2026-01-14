const form = document.getElementById("form");
const input = document.getElementById("content");
const list = document.getElementById("list");
const statusEl = document.getElementById("status");

async function fetchTodos() {
  statusEl.textContent = "불러오는 중...";
  const res = await fetch("/api/todos");
  const todos = await res.json();
  render(todos);
  statusEl.textContent = `총 ${todos.length}개`;
}

function render(todos) {
  list.innerHTML = "";
  for (const t of todos) {
    const li = document.createElement("li");
    const date = new Date(t.createdAt).toLocaleString();
    li.textContent = t.content;

    const meta = document.createElement("span");
    meta.className = "meta";
    meta.textContent = `(${date})`;
    li.appendChild(meta);

    list.appendChild(li);
  }
}

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

fetchTodos();
