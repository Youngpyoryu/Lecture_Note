require("dotenv").config();
const express = require("express");
const mongoose = require("mongoose");

const app = express();
app.use(express.json());
app.use(express.static("public"));

// =========================
// (05-1) Todo Schema: done 필드 추가
// =========================
const TodoSchema = new mongoose.Schema(
  {
    content: { type: String, required: true, trim: true },
    done: { type: Boolean, default: false },
  },
  { timestamps: true }
);

const Todo = mongoose.model("Todo", TodoSchema, "todos");

// =========================
// API
// =========================

// (목록) GET /api/todos
app.get("/api/todos", async (req, res) => {
  const todos = await Todo.find().sort({ createdAt: -1 });
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

// (04) 삭제) DELETE /api/todos/:id
app.delete("/api/todos/:id", async (req, res) => {
  const deleted = await Todo.findByIdAndDelete(req.params.id);
  if (!deleted) return res.status(404).json({ message: "Not found" });

  console.log("\n=== Delete TodoTask ===");
  console.table([{ id: String(deleted._id), content: deleted.content }]);

  res.json({ ok: true });
});

// =========================
// (05-2) 토글) PATCH /api/todos/:id/toggle
// =========================
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
    console.log(`05 server: http://localhost:${PORT}/05_index.html`)
  );
}

start().catch((e) => {
  console.error("ERROR:", e.message);
  process.exit(1);
});
