const express = require('express');
const app = express();

let posts = []; // 게시물 리스트로 사용할 빈 리스트 할당.

// req.body를 사용하려면 JSON 데이터를 파싱해야 합니다.
app.use(express.json()); // JSON 미들웨어 활성화

// POST 요청에 전달된 타입이 application/x-www-form-urlencoded인 경우 파싱
app.use(express.urlencoded({ extended: true })); // URL 인코딩된 데이터 파싱

// GET 요청: 게시물 리스트를 반환
app.get('/', (req, res) => {
  res.json(posts); // 게시물 리스트를 JSON 형식으로 보여줌
});

// POST 요청 처리: 새로운 게시물 추가
app.post('/posts', (req, res) => {
  const { title, name, text } = req.body; // HTTP 요청 body 데이터를 변수에 할당

  // 게시물 리스트에 새로운 게시물 추가
  const newPost = { id: posts.length + 1, title, name, text, createDt: new Date() };
  posts.push(newPost);
  res.json(newPost); // 새로 추가된 게시물 정보를 응답으로 반환
});

// DELETE 요청 처리: 게시물 삭제
app.delete('/posts/:id', (req, res) => {
  const id = parseInt(req.params.id); // app.delete에 설정한 path 경로에서 id 값을 가져옴
  const filteredPosts = posts.filter(post => post.id !== id); // 삭제 필터링
  const isLengthChanged = posts.length !== filteredPosts.length; // 삭제 확인
  posts = filteredPosts;

  if (isLengthChanged) {
    res.json("OK"); // 삭제 성공
  } else {
    res.json("NOT CHANGED"); // 삭제 실패 (ID가 존재하지 않음)
  }
});

// 서버를 포트 3000에서 리슨 시작
app.listen(3000, () => {
  console.log('서버가 포트 3000에서 시작되었습니다.');
});
