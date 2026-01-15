require("dotenv").config();
const express = require("express");
const mongoose = require("mongoose");

const app = express();
app.use(express.json());
app.use(express.static("public"));

const TodoSchema = new mongoose.Schema(
  {
    content: {
      type: String,
      required: [true, "내용(content)은 필수입니다."],
      trim: true,
      minlength: [1, "내용은 1자 이상이어야 합니다."],
      maxlength: [50, "내용은 50자 이하여야 합니다."],
    },
    done: { type: Boolean, default: false },
  },
  { timestamps: true }
);

const Todo = mongoose.model("Todo", TodoSchema, "todos");

app.get("/api/todos", async (req, res) => {
  const q = (req.query.q || "").trim();
  const filter = q ? { content: { $regex: q, $options: "i" } } : {};
  const todos = await Todo.find(filter).sort({ createdAt: -1 });
  res.json(todos);
});

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
    const msg =
      e?.errors?.content?.message ||
      e.message ||
      "입력값이 올바르지 않습니다.";
    res.status(400).json({ message: msg });
  }
});

app.delete("/api/todos/:id", async (req, res) => {
  const deleted = await Todo.findByIdAndDelete(req.params.id);
  if (!deleted) return res.status(404).json({ message: "Not found" });

  console.log("\n=== Delete TodoTask ===");
  console.table([{ id: String(deleted._id), content: deleted.content }]);

  res.json({ ok: true });
});

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
    console.log(`07 server: http://localhost:${PORT}/07_index.html`)
  );
}

start().catch((e) => {
  console.error("ERROR:", e.message);
  process.exit(1);
});
