// ex01_params.js
const express = require("express");
const app = express();

app.get("/users/:id", (req, res) => {
  res.json({ userId: req.params.id });
});

app.get("/search", (req, res) => {
  const { q = "", page = "1" } = req.query;
  res.json({ q, page: Number(page) });
});

app.listen(3000, () => console.log("ex01 listening on 3000"));