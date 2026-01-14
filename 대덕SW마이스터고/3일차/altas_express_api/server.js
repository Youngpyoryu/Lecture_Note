// server.js
require("dotenv").config();
const express = require("express");
const { ObjectId } = require("mongodb");
const { connectDB, closeDB } = require("./db");

const app = express();
app.use(express.json());

// Health
app.get("/health", async (req, res) => {
  res.json({ ok: true });
});

// Create
app.post("/people", async (req, res) => {
  try {
    const col = await connectDB();
    const { name, age } = req.body ?? {};

    if (!name) return res.status(400).json({ error: "name is required" });

    const doc = { name, age: age ?? null, createdAt: new Date() };
    const r = await col.insertOne(doc);

    res.status(201).json({ insertedId: r.insertedId, ...doc });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Read (optional filter: ?name=)
app.get("/people", async (req, res) => {
  try {
    const col = await connectDB();
    const { name } = req.query;

    const filter = name ? { name } : {};
    const docs = await col.find(filter).sort({ createdAt: -1 }).limit(50).toArray();

    res.json({ count: docs.length, docs });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Update by id
app.patch("/people/:id", async (req, res) => {
  try {
    const col = await connectDB();
    const { id } = req.params;
    const { name, age } = req.body ?? {};

    const set = {};
    if (name !== undefined) set.name = name;
    if (age !== undefined) set.age = age;
    set.updatedAt = new Date();

    const r = await col.updateOne(
      { _id: new ObjectId(id) },
      { $set: set }
    );

    if (r.matchedCount === 0) return res.status(404).json({ error: "not found" });
    res.json({ matched: r.matchedCount, modified: r.modifiedCount });
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

// Delete by id
app.delete("/people/:id", async (req, res) => {
  try {
    const col = await connectDB();
    const { id } = req.params;

    const r = await col.deleteOne({ _id: new ObjectId(id) });
    res.json({ deleted: r.deletedCount });
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

const PORT = Number(process.env.PORT ?? 3000);
app.listen(PORT, async () => {
  console.log(`API running: http://localhost:${PORT}`);
  // 서버 시작 시점에 미리 연결해두고 싶으면 아래 호출
  await connectDB();
});

// 종료 처리(선택)
process.on("SIGINT", async () => {
  await closeDB();
  process.exit(0);
});
