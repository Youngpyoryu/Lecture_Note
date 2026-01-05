// node 05_server_async_io.js
const http = require("http");
const fs = require("fs");

const server = http.createServer((req, res) => {
  if (req.url === "/slow-io") {
    // I/O 비동기: 파일 읽기(대기) 동안 이벤트루프는 다른 요청 처리 가능
    fs.readFile(__filename, "utf8", (err, data) => {
      if (err) {
        res.statusCode = 500;
        return res.end("error");
      }
      res.setHeader("Content-Type", "text/plain; charset=utf-8");
      res.end("read done, len=" + data.length);
    });
    return;
  }

  if (req.url === "/fast") {
    res.end("fast ok");
    return;
  }

  res.statusCode = 404;
  res.end("not found");
});

server.listen(3000, () => console.log("http://localhost:3000"));
