// node 01_blocking_cpu.js
function busyWait(ms) {
  const end = Date.now() + ms;
  while (Date.now() < end) {} // CPU를 계속 점유
}

console.log("start");

setTimeout(() => console.log("timer fired (should be ~0ms, but delayed)"), 0);

console.log("busyWait 2000ms...");
busyWait(2000);

console.log("end");
