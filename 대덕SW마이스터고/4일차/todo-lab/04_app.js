require("dotenv").config();
const express = require("express");
const mongoose = require("mongoose");

const app = express();

/* =========================
 * (03단계에서 이미 있던 설정)
 * - JSON 요청 body를 읽기 위해 express.json() 사용
 * - public 폴더의 HTML/JS를 브라우저에 제공하기 위해 static 사용
 * ========================= */
app.use(express.json());
app.use(express.static("public"));

/* =========================
 * (03단계 모델: Todo 스키마)
 * - 04단계에서는 스키마 변경 없음
 * - content 하나만 저장하는 최소 모델
 * ========================= */
const TodoSchema = new mongoose.Schema(
  { content: { type: String, required: true, trim: true } },
  { timestamps: true }
);
const Todo = mongoose.model("Todo", TodoSchema, "todos");

/* =========================
 * (03단계 API 2개: 목록 조회 + 생성)
 * ========================= */

// (03) Read all: 전체 목록
app.get("/api/todos", async (req, res) => {
  const todos = await Todo.find().sort({ createdAt: -1 });
  res.json(todos);
});

// (03) Create: 1개 생성
app.post("/api/todos", async (req, res) => {
  try {
    const todo = await Todo.create({ content: req.body.content });

    // (03) 서버 콘솔에 "저장됨"을 표로 출력
    console.log("\n=== Success!! Save New TodoTask ===");
    console.table([
      {
        id: String(todo._id),
        content: todo.content,
        date: todo.createdAt.toISOString(),
      },
    ]);

    res.status(201).json(todo);
  } catch (e) {
    res.status(400).json({ message: e.message });
  }
});

/* ==========================================================
 *  (04단계에서 '새로 추가된' 핵심: Delete API
 *
 * - 목적: 브라우저에서 "삭제" 버튼을 누르면
 *         해당 todo 문서를 MongoDB에서 삭제하고 응답을 준다.
 * - URL: DELETE /api/todos/:id
 * - 동작:
 *   1) req.params.id로 삭제할 문서 id를 받는다
 *   2) Todo.findByIdAndDelete로 DB에서 실제 삭제한다
 *   3) 삭제 성공이면 서버 콘솔에 삭제된 항목을 표로 출력한다
 *   4) { ok: true }를 응답한다
 * - 시각적 확인:
 *   - 브라우저 목록에서 즉시 사라짐
 *   - 서버 콘솔에 "Delete TodoTask" 표가 찍힘
 * ========================================================== */
app.delete("/api/todos/:id", async (req, res) => {
  const deleted = await Todo.findByIdAndDelete(req.params.id);

  // (04) 존재하지 않는 id면 404
  if (!deleted) return res.status(404).json({ message: "Not found" });

  // (04) 서버 콘솔 표 출력(삭제 확인용)
  console.log("\n=== Delete TodoTask ===");
  console.table([
    {
      id: String(deleted._id),
      content: deleted.content,
    },
  ]);

  // (04) 삭제 성공 응답
  res.json({ ok: true });
});

/* =========================
 * 서버 시작(03단계와 동일)
 * ========================= */
async function start() {
  const uri = process.env.MONGODB_URI;
  if (!uri) throw new Error("MONGODB_URI가 .env에 없습니다.");

  await mongoose.connect(uri);
  console.log("MongoDB connected");

  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () =>
    console.log(`04 server: http://localhost:${PORT}/04_index.html`)
  );
}

start().catch((e) => {
  console.error("ERROR:", e.message);
  process.exit(1);
});
