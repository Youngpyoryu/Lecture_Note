// 07_rps.js
// 가위바위보(점수판) - Node.js readline
// 입력: 가위/바위/보 또는 1/2/3, 종료: exit

const readline = require("readline");

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

const mapInput = (s) => {
  const t = s.trim().toLowerCase();
  if (t === "exit" || t === "quit") return "EXIT";
  if (t === "1" || t === "가위" || t === "scissors") return "가위";
  if (t === "2" || t === "바위" || t === "rock") return "바위";
  if (t === "3" || t === "보" || t === "paper") return "보";
  return null;
};

const choices = ["가위", "바위", "보"];
const randomChoice = () => choices[Math.floor(Math.random() * choices.length)];

const result = (user, cpu) => {
  if (user === cpu) return "DRAW";
  if (
    (user === "가위" && cpu === "보") ||
    (user === "바위" && cpu === "가위") ||
    (user === "보" && cpu === "바위")
  ) return "WIN";
  return "LOSE";
};

let win = 0, draw = 0, lose = 0;

console.log("가위바위보 시작!");
console.log("입력: 1=가위, 2=바위, 3=보 (또는 가위/바위/보). 종료: exit");
process.stdout.write("> ");

rl.on("line", (line) => {
  const user = mapInput(line);
  if (user === "EXIT") {
    console.log(`종료! 최종 전적: ${win}승 ${draw}무 ${lose}패`);
    rl.close();
    return;
  }
  if (!user) {
    console.log("잘못된 입력입니다. 1/2/3 또는 가위/바위/보를 입력하세요.");
    process.stdout.write("> ");
    return;
  }

  const cpu = randomChoice();
  const r = result(user, cpu);

  if (r === "WIN") win++;
  else if (r === "DRAW") draw++;
  else lose++;

  console.log(`나: ${user} | 컴퓨터: ${cpu} => ${r === "WIN" ? "승" : r === "DRAW" ? "무" : "패"}`);
  console.log(`현재 전적: ${win}승 ${draw}무 ${lose}패`);
  process.stdout.write("> ");
});

rl.on("close", () => process.exit(0));
