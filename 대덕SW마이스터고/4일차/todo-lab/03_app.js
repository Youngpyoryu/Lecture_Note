require("dotenv").config();
const express = require("express");
const mongoose = require("mongoose");

const app = express();
app.use(express.json());
app.use(express.static("public"));

// Todo 스키마(최소)
const TodoSchema = new mongoose.Schema(
  { content: { type: String, required: true, trim: true } },
  { timestamps: true }
);
const Todo = mongoose.model("Todo", TodoSchema, "todos");

// (A) 목록 조회
app.get("/api/todos", async (req, res) => {
  const todos = await Todo.find().sort({ createdAt: -1 });
  res.json(todos);
});

// (B) 추가
app.post("/api/todos", async (req, res) => {
  try {
    const todo = await Todo.create({ content: req.body.content });

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

async function start() {
  const uri = process.env.MONGODB_URI;
  if (!uri) throw new Error("MONGODB_URI가 .env에 없습니다.");

  await mongoose.connect(uri);
  console.log("MongoDB connected");

  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => console.log(`03 server: http://localhost:${PORT}/03_index.html`));
}

start().catch((e) => {
  console.error("ERROR:", e.message);
  process.exit(1);
});
