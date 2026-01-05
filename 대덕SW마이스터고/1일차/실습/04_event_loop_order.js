// node 04_event_loop_order.js
console.log("start");

process.nextTick(() => console.log("nextTick"));
Promise.resolve().then(() => console.log("promise then"));

setTimeout(() => console.log("setTimeout 0"), 0);
setImmediate(() => console.log("setImmediate"));

console.log("end");
