// chatbot.js
// 실행: node chatbot.js

const readline = require("readline");

// 미리 정의된 질문-응답 데이터
const responses = {
  안녕: "안녕하세요! 챗봇입니다. 무엇을 도와드릴까요?",
  이름이뭐야: "저는 간단한 챗봇입니다. 이름은 없어요!",
  시간이몇시야: `지금은 ${new Date().toLocaleTimeString()}입니다.`,
  잘가: "안녕히 가세요! 다음에 또 만나요!",
};

// 입력 인터페이스 생성
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

// 사용자와 챗봇의 대화
function startChat() {
  rl.question("사용자: ", (input) => {
    const cleaned = input.replace(/\s+/g, ""); // 공백 제거(예: "이름이 뭐야" -> "이름이뭐야")
    const response = responses[cleaned] || "죄송하지만, 이해하지 못했어요.";

    console.log(`챗봇: ${response}`);

    if (cleaned === "잘가") {
      rl.close();
    } else {
      startChat();
    }
  });
}

console.log("챗봇과 대화를 시작합니다. (종료하려면 '잘 가'를 입력하세요)");
startChat();
