require("dotenv").config();
const mongoose = require("mongoose");

async function main() {
  const uri = process.env.MONGODB_URI;
  if (!uri) throw new Error("MONGODB_URI가 .env에 없습니다.");

  await mongoose.connect(uri);

  // strict: "throw" => 스키마에 없는 필드(extra)는 에러로 차단
  const User = mongoose.model(
    "UserMin",
    new mongoose.Schema(
      { age: { type: Number, required: true } },
      { strict: "throw" }
    ),
    "t1_mongoose"
  );

  await User.deleteMany({});

  console.log("\n[Mongoose] 저장 시도 (막혀야 정상):");
  try {
    await User.create({ age: "not number", extra: 123 });
    console.log("Unexpected: saved (이 줄이 나오면 목표와 다름)");
  } catch (e) {
    console.log("Blocked:", e.message);
  }

  await mongoose.disconnect();
}

main().catch((e) => {
  console.error("ERROR:", e.message);
  process.exit(1);
});
