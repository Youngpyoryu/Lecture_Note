require("dotenv").config();
const express = require("express");
const mongoose = require("mongoose");

const app = express();
app.use(express.static("public"));

// 1) Todo 스키마(아주 최소)
const TodoSchema = new mongoose.Schema(
  { content: { type: String, required: true, trim: true } },
  { timestamps: true }
);

// 2) 모델
const Todo = mongoose.model("Todo", TodoSchema, "todos");

// 3) 테스트용 라우트: 접속하면 DB에 1개 저장하고 콘솔에 표 출력
app.get("/seed", async (req, res) => {
  const todo = await Todo.create({ content: "02 seed todo" });

  console.log("\n=== Success!! Save New TodoTask ===");
  console.table([
    {
      id: String(todo._id),
      content: todo.content,
      date: todo.createdAt.toISOString(),
    },
  ]);

  res.send("saved one todo. check server console.");
});

app.get("/health", (req, res) => res.send("OK"));

async function start() {
  const uri = process.env.MONGODB_URI;
  if (!uri) throw new Error("MONGODB_URI가 .env에 없습니다.");

  await mongoose.connect(uri);
  console.log("MongoDB connected");

  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => console.log(`02 server: http://localhost:${PORT}`));
}

start().catch((e) => {
  console.error("ERROR:", e.message);
  process.exit(1);
});
