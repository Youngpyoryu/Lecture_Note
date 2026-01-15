require("dotenv").config();
const { MongoClient } = require("mongodb");

async function main() {
  const uri = process.env.MONGODB_URI;
  if (!uri) throw new Error("MONGODB_URI가 .env에 없습니다.");

  const client = new MongoClient(uri);
  await client.connect();

  // DB 이름을 지정하지 않음 -> Atlas 기본 DB로 저장(보통 test)
  const db = client.db();
  const col = db.collection("t1_native");

  await col.deleteMany({});

  await col.insertOne({
    age: "not number",
    role: "godmode",
    extra: 123,
  });

  const stored = await col.findOne({});
  console.log("\n[Native Driver] 저장 결과 (그대로 들어가야 함):");
  console.log(stored);

  await client.close();
}

main().catch((e) => {
  console.error("ERROR:", e.message);
  process.exit(1);
});
