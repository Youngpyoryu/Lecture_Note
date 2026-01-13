// express_test.js
const express = require("express"); // Express 프레임워크 모듈을 불러온다
const app = express(); // Express 애플리케이션(서버 인스턴스)을 생성한다
const port = 3000; // 서버가 대기(listen)할 포트 번호를 지정한다

app.get("/", (req, res) => { // "/"로 들어오는 GET 요청에 대한 처리 함수를 등록한다
  res.setHeader("Content-Type", "text/html; charset=utf-8"); // 응답의 콘텐츠 타입과 인코딩(UTF-8)을 설정한다
  res.send("헬로 Express"); // 클라이언트에게 본문 내용을 전송하고 응답을 종료한다
});

app.listen(port, () => { // 지정한 포트에서 서버를 시작하고 요청을 받을 준비를 한다
  console.log(`START SERVER: use ${port}`); // 서버가 정상적으로 시작됐음을 콘솔에 출력한다
});

//mkdir express-lab && cd express-lab
//npm init -y
//npm i express