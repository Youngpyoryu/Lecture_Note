// 08_updown.js
// 업다운(횟수 제한) - Node.js readline
// 규칙: 1~100 랜덤 숫자, 7번 안에 맞추기, 종료: exit

const readline = require("readline");
const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

const secret = Math.floor(Math.random() * 100) + 1;
const MAX_TRIES = 7;
let tries = 0;

console.log("업다운 게임 시작!");
console.log(`1~100 사이 숫자를 맞춰보세요. 기회는 ${MAX_TRIES}번입니다. 종료: exit`);
process.stdout.write("> ");

rl.on("line", (line) => {
  const t = line.trim().toLowerCase();

  if (t === "exit" || t === "quit") {
    console.log("종료합니다.");
    rl.close();
    return;
  }

  const n = Number(t);
  if (!Number.isInteger(n) || n < 1 || n > 100) {
    console.log("1~100 사이의 정수를 입력하세요.");
    process.stdout.write("> ");
    return;
  }

  tries++;
  const left = MAX_TRIES - tries;

  if (n === secret) {
    console.log(`정답! (${tries}번째 시도)`);
    rl.close();
    return;
  }

  console.log(n < secret ? "UP" : "DOWN");
  console.log(`남은 기회: ${left}번`);

  if (left <= 0) {
    console.log(`실패! 정답은 ${secret} 입니다.`);
    rl.close();
    return;
  }

  process.stdout.write("> ");
});

rl.on("close", () => process.exit(0));
