import http from "http";

const server = http.createServer((req, res) => {
  // URL과 메서드 확인
  const { method, url } = req;

  // 라우팅
  if (method === "GET" && url === "/") {
    res.writeHead(200, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("Hello Node!\n");
    return;
  }

  if (method === "GET" && url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
    res.end(JSON.stringify({ ok: true }));
    return;
  }

  res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
  res.end("Not Found\n");
});

server.listen(3000, () => {
  console.log("Listening on http://localhost:3000");
});
