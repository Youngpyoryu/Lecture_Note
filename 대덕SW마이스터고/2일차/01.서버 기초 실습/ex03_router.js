// ex03_router.js
const express = require("express");
const app = express();
app.use(express.json());

const router = express.Router();

router.get("/health", (req, res) => res.json({ ok: true }));
router.get("/posts/:id", (req, res) => res.json({ id: req.params.id }));
router.post("/posts", (req, res) => res.status(201).json({ created: true, body: req.body }));

app.use("/api", router);

app.listen(3000, () => console.log("ex04 listening on 3000"));
