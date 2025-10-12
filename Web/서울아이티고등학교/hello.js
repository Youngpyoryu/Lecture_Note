const http = require('http'); //http 객체 생성
//모듈을 읽어오는 함수.
let count=0;
//숫자를 카운트 하려고 한것.
const server = http.createServer((req,res) => { //서버 객체 생성
    //서버 인스턴스 만든 함수.
    log(count);
    // 전역 변수 count를 사용하여서 간단한 로그를 남기는 것.
    res.statusCode=200;
    // 200(성공), 404(Not found, 페이지를 찾을 수 없음)
    res.setHeader("Content-Type", "text/plain");
    //HTTP 요청/응답에 대한 부가정보를 설정할 수 있음.
    // text/plain : 텍스트를 평문으로 해석하겠습니다.
    // text/html : 텍스트를 html로 해석하겠다.
    res.write("Hello\n");
    //응답으로는 hello\n을 보내줌.
    setTimeout(() =>{
        res.end('Node.js');
    }, 2000);
    //2000이라는 숫자는 밀리초이며 해당시간이 지나면 콜백 함수를 실행.
    //여기서는 2초후 Node.js 응답으로 주고 받음.
   });

   function log(count){
    console.log((count +=1));
   }

server.listen(8000, () => console.log('Hello Node.js'));
//사용할 포트번호 8000, IP가 생략되었으므로 기본값은 localhost or 127.0.0.1:8000