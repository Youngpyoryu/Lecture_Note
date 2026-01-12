// items_api.js  (목적: 아이템/상품 CRUD)
const express = require("express");
const app = express();
const port = 3000;

app.use(express.json()); // JSON body 파싱

// 메모리 "DB" (아이템 목록)
let items = [
  { id: 1, name: "apple", price: 1000 },
  { id: 2, name: "banana", price: 2000 },
];
let nextId = 3;

// 아이템 생성 (CREATE)
app.post("/items", (req, res) => {
  const { name, price } = req.body || {};
  if (!name || typeof price !== "number") {
    return res.status(400).json({ error: "name, price(number) required" });
  }
  const item = { id: nextId++, name, price };
  items.push(item);
  res.status(201).json(item);
});

// 아이템 전체 조회 (READ)
app.get("/items", (req, res) => {
  res.json(items);
});

// 아이템 단건 조회 (READ)
app.get("/items/:id", (req, res) => {
  const item = items.find((x) => x.id === Number(req.params.id));
  if (!item) return res.status(404).json({ error: "item not found" });
  res.json(item);
});

// 아이템 전체 수정 (PUT) - name/price 둘 다 보내는 걸 권장
app.put("/items/:id", (req, res) => {
  const item = items.find((x) => x.id === Number(req.params.id));
  if (!item) return res.status(404).json({ error: "item not found" });

  const { name, price } = req.body || {};
  if (!name || typeof price !== "number") {
    return res.status(400).json({ error: "name, price(number) required" });
  }

  item.name = name;
  item.price = price;
  res.json(item);
});

// 아이템 일부 수정 (PATCH) - 일부만 보내도 됨
app.patch("/items/:id", (req, res) => {
  const item = items.find((x) => x.id === Number(req.params.id));
  if (!item) return res.status(404).json({ error: "item not found" });

  const { name, price } = req.body || {};
  if (name !== undefined) item.name = name;
  if (price !== undefined) {
    if (typeof price !== "number") return res.status(400).json({ error: "price must be number" });
    item.price = price;
  }
  res.json(item);
});

// 아이템 삭제 (DELETE)
app.delete("/items/:id", (req, res) => {
  const before = items.length;
  items = items.filter((x) => x.id !== Number(req.params.id));
  if (items.length === before) return res.status(404).json({ error: "item not found" });
  res.sendStatus(204); // 성공(본문 없음)
});

app.listen(port, () => {
  console.log(`Items API running at http://localhost:${port}`);
});
