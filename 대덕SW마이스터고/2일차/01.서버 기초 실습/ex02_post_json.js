// ex02_post_json.js
const express = require("express");
const app = express();

app.use(express.json()); // JSON body 파싱

app.post("/items", (req, res) => {
  const { name, price } = req.body || {};
  if (!name || typeof price !== "number") {
    return res.status(400).json({ ok: false, error: "name, price(number) required" });
  }
  res.status(201).json({ ok: true, item: { name, price } });
});

app.listen(3000, () => console.log("ex02 listening on 3000"));

