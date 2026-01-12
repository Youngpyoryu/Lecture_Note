// ex04_crud.js
const express = require("express");
const app = express();
app.use(express.json());

let items = []; // 메모리 저장소
let id = 1;

// C
app.post("/items", (req, res) => {
  const item = { id: id++, ...req.body };
  items.push(item);
  res.status(201).json(item);
});

// R
app.get("/items", (req, res) => res.json(items));

// U
app.patch("/items/:id", (req, res) => {
  const i = items.findIndex((x) => x.id === Number(req.params.id));
  if (i === -1) return res.sendStatus(404);
  items[i] = { ...items[i], ...req.body };
  res.json(items[i]);
});

// D
app.delete("/items/:id", (req, res) => {
  items = items.filter((x) => x.id !== Number(req.params.id));
  res.sendStatus(204);
});

app.listen(3000, () => console.log("http://localhost:3000"));