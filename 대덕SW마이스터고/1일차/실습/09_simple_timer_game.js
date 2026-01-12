// 09_simple_timer_game.js
// 간단 반응속도 게임(Enter 타이밍)
// 규칙: "NOW!"가 뜨면 Enter를 최대한 빨리 누르기
// 주의: 너무 빨리 누르면 실패
// 종료: exit

const readline = require("readline");
const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

let state = "WAIT_START"; // WAIT_START -> WAIT_NOW
let startTime = 0;
let timerId = null;

console.log("반응속도 게임!");
console.log("규칙: 시작 후 기다리다가 'NOW!'가 나오면 Enter를 누르세요.");
console.log("너무 빨리 누르면 실패합니다.");
console.log("시작: Enter | 종료: exit");

process.stdout.write("> ");

function scheduleNow() {
  // 1~3초 랜덤 대기 후 NOW 출력
  const delayMs = 1000 + Math.floor(Math.random() * 2000);

  timerId = setTimeout(() => {
    state = "WAIT_NOW";
    startTime = Date.now();
    console.log("\nNOW! (지금 Enter)");
    process.stdout.write("> ");
  }, delayMs);
}

rl.on("line", (line) => {
  const input = line.trim().toLowerCase();

  if (input === "exit" || input === "quit") {
    console.log("종료합니다.");
    rl.close();
    return;
  }

  // 사용자는 Enter를 누르는 걸 목표로 하므로, 아무 글자 입력도 Enter로 처리
  if (state === "WAIT_START") {
    console.log("준비... 기다리세요.");
    state = "WAIT_NOW_PENDING";
    scheduleNow();
    return;
  }

  if (state === "WAIT_NOW_PENDING") {
    // NOW! 나오기 전에 눌렀으면 실패
    clearTimeout(timerId);
    timerId = null;
    console.log("너무 빨랐습니다! 실패. 다시 시작하려면 Enter.");
    state = "WAIT_START";
    process.stdout.write("> ");
    return;
  }

  if (state === "WAIT_NOW") {
    const ms = Date.now() - startTime;
    console.log(`반응속도: ${ms} ms`);
    console.log("다시 하려면 Enter.");
    state = "WAIT_START";
    process.stdout.write("> ");
    return;
  }
});

rl.on("close", () => process.exit(0));
