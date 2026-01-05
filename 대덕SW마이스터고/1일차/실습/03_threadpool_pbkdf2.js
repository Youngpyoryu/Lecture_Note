//# windows powershell
//$env:UV_THREADPOOL_SIZE=1; node 03_threadpool_pbkdf2.js
//$env:UV_THREADPOOL_SIZE=4; node 03_threadpool_pbkdf2.js
const crypto = require("crypto");

const jobs = 4;
const start = Date.now();

console.log("UV_THREADPOOL_SIZE =", process.env.UV_THREADPOOL_SIZE || "(default)");
console.log("starting", jobs, "pbkdf2 jobs...");

for (let i = 1; i <= jobs; i++) {
  crypto.pbkdf2("pw", "salt", 200_000, 32, "sha256", () => {
    console.log(`job ${i} done at +${Date.now() - start}ms`);
  });
}
