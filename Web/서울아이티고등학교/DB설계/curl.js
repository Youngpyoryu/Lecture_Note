const express = require('express') //express 모듈을 로딩
const app = express() //Express 애플리케이션 생성
let posts = [] //게시글 리스트로 사용할 posts에 빈 리스트 할당.

//req.body를 사용하려면 JSON 미들웨어를 사용해야 합니다.
// 사용안하면 undefined로 반환
app.use(express.json()); //JSON 미들웨어 활성화.

//POST 요청시 컨텐트 타입이 application/x-www-from-urlencoded인 경우 파싱
app.use(express.urlencoded({extended:true})) //URL 인코딩된 데이터 파싱

//GET 요청 처리 : 게시글 목록 반환
app.get("/", (req,res) =>{
  res.json(posts); //게시글 리스트 JSON 형식으로 보여줌.
})

//POST 요청 처리 : 새로운 게시글 추가
app.post("/posts", (req,res) => {
  const {title, name, text} = res.body; //HTTP 요청의 body 데이터를 변수에 할당

  //게시글 리스트에 새로운 게시글 정보 추가
  const newPost = {id : posts.length+1, title, name, text, createDt : new Date()};
  posts.push(newPost);
  res.json(newPost); //새로운 추가된 게시글 정보를 응답으로 반환
});

//DELETE 요청 처리 : 게시글 삭제
app.delete("/posts/:id", (req,res) => {
  const id = parseInt(req.params.id); // app.delete에 설정한 path 정보에서 id값을 가져옴.
  const filteredPosts = posts.filter(post => posts.id !==id) //글 삭제 로직
  const isLengthChanged = posts.length !==filteredPosts.length; //삭제 확인
  posts = filteredPosts;

  if (isLengthChanged){
    res.json("OK") //삭제 성공
  } else {
    res.json("NOT CHANGED") //삭제 실패(ID가 존재하지 않음)
  }
})

app.listen(3000, () => console.log("서버가 포트 3000에서 시작되었습니다."))