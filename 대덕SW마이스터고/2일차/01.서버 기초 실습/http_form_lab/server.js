// server.js
// 실행: node server.js
// 접속: http://localhost:3000

const http = require("http");
const url = require("url");
const fs = require("fs");
const path = require("path");

// x-www-form-urlencoded 파서 (간단 버전)
function parseFormUrlEncoded(body) {
  const params = new URLSearchParams(body);
  const obj = {};

  for (const [k, v] of params.entries()) {
    // checkbox처럼 같은 name이 여러 번 올 수 있음 -> 배열로 처리
    if (obj[k] === undefined) obj[k] = v;
    else if (Array.isArray(obj[k])) obj[k].push(v);
    else obj[k] = [obj[k], v];
  }
  return obj;
}

const server = http.createServer((req, res) => {
  const { pathname } = url.parse(req.url, true);

  // 1) GET / : index.html 반환
  if (req.method === "GET" && pathname === "/") {
    const filePath = path.join(__dirname, "index.html");
    const html = fs.readFileSync(filePath, "utf-8");
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    res.end(html);
    return;
  }

  // 2) GET /user : 간단 텍스트 응답
  if (req.method === "GET" && pathname === "/user") {
    res.writeHead(200, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("[user] name: andy, age: 30");
    return;
  }

  // 3) GET /feed : 간단 HTML 응답
  if (req.method === "GET" && pathname === "/feed") {
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    res.end(`
      <h1>Feed</h1>
      <ul>
        <li>picture1</li>
        <li>picture2</li>
        <li>picture3</li>
      </ul>
    `);
    return;
  }

  // 4) POST /order : 폼 데이터 수신 후 결과 페이지 반환
  if (req.method === "POST" && pathname === "/order") {
    let body = "";

    req.on("data", (chunk) => {
      body += chunk.toString();
      // 너무 큰 요청 방지(간단)
      if (body.length > 1e6) req.destroy();
    });

    req.on("end", () => {
      const data = parseFormUrlEncoded(body);

      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      res.end(`
        <h1>주문 접수 완료</h1>
        <p><strong>고객명</strong>: ${data.name ?? ""}</p>
        <p><strong>전화번호</strong>: ${data.phone ?? ""}</p>
        <p><strong>Email</strong>: ${data.email ?? ""}</p>
        <p><strong>피자</strong>: ${data.pizza ?? ""}</p>
        <p><strong>사이즈</strong>: ${data.size ?? ""}</p>
        <p><strong>토핑</strong>: ${
          Array.isArray(data.topping) ? data.topping.join(", ") : (data.topping ?? "")
        }</p>
        <p><strong>희망배송시간</strong>: ${data.time ?? ""}</p>
        <p><strong>요청사항</strong>: ${data.request ?? ""}</p>
        <hr />
        <a href="/">다시 주문하기</a>
      `);
    });

    return;
  }

  // 5) 나머지: 404
  res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
  res.end("404 page not found");
});

server.listen(3000, () => {
  console.log("Server running: http://localhost:3000");
  console.log("Try: /user , /feed , /");
});
