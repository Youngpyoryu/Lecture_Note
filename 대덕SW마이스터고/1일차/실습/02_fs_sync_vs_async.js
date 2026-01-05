// node 02_fs_sync_vs_async.js
const fs = require("fs");

console.log("A) async readFile start");
fs.readFile(__filename, "utf8", (err, data) => {
  if (err) throw err;
  console.log("A) async readFile done (len)", data.length);
});

console.log("B) sync readFileSync start");
const data2 = fs.readFileSync(__filename, "utf8");
console.log("B) sync readFileSync done (len)", data2.length);

console.log("C) end of script");
