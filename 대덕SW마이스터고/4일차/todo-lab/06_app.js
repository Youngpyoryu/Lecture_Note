require("dotenv").config();
const express = require("express");
const mongoose = require("mongoose");

const app = express();
app.use(express.json());
app.use(express.static("public"));

// Todo Schema (05 유지)
const TodoSchema = new mongoose.Schema(
  {
    content: { type: String, required: true, trim: true },
    done: { type: Boolean, default: false },
  },
  { timestamps: true }
);
const Todo = mongoose.model("Todo", TodoSchema, "todos");

// =========================
// (06) GET /api/todos?q=키워드
// - q가 있으면 content에 q가 포함된 것만
// - createdAt 최신순 정렬 유지
// =========================
app.get("/api/todos", async (req, res) => {
  const q = (req.query.q || "").trim();

  const filter = q
    ? { content: { $regex: q, $options: "i" } } // i: 대소문자 무시
    : {};

  const todos = await Todo.find(filter).sort({ createdAt: -1 });
  res.json(todos);
});

// (추가) POST /api/todos
app.post("/api/todos", async (req, res) => {
  try {
    const todo = await Todo.create({ content: req.body.content });

    console.log("\n=== Success!! Save New TodoTask ===");
    console.table([
      {
        id: String(todo._id),
        content: todo.content,
        done: todo.done,
        date: todo.createdAt.toISOString(),
      },
    ]);

    res.status(201).json(todo);
  } catch (e) {
    res.status(400).json({ message: e.message });
  }
});

// (삭제) DELETE /api/todos/:id
app.delete("/api/todos/:id", async (req, res) => {
  const deleted = await Todo.findByIdAndDelete(req.params.id);
  if (!deleted) return res.status(404).json({ message: "Not found" });

  console.log("\n=== Delete TodoTask ===");
  console.table([{ id: String(deleted._id), content: deleted.content }]);

  res.json({ ok: true });
});

// (토글) PATCH /api/todos/:id/toggle
app.patch("/api/todos/:id/toggle", async (req, res) => {
  const todo = await Todo.findById(req.params.id);
  if (!todo) return res.status(404).json({ message: "Not found" });

  todo.done = !todo.done;
  await todo.save();

  console.log("\n=== Toggle TodoTask ===");
  console.table([{ id: String(todo._id), done: todo.done, content: todo.content }]);

  res.json(todo);
});

async function start() {
  const uri = process.env.MONGODB_URI;
  if (!uri) throw new Error("MONGODB_URI가 .env에 없습니다.");

  await mongoose.connect(uri);
  console.log("MongoDB connected");

  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () =>
    console.log(`06 server: http://localhost:${PORT}/06_index.html`)
  );
}

start().catch((e) => {
  console.error("ERROR:", e.message);
  process.exit(1);
});
