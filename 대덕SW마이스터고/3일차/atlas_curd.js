const { MongoClient, ServerApiVersion } = require("mongodb");

// 1) Atlas SRV URI (비밀번호만 교체)
const uri =
  "mongodb+srv://test:<PASSWORD>@cluster0.xqqsn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";

async function main() {
  const client = new MongoClient(uri, { serverApi: ServerApiVersion.v1 });

  try {
    // A) 연결 확인 (ping)
    await client.connect();
    await client.db("admin").command({ ping: 1 });
    console.log("1) 연결 확인: ping 성공");

    // B) DB/Collection 선택
    const db = client.db("test");
    const col = db.collection("person");

    // C) Insert (중복 방지를 위해 이름에 timestamp)
    const name = `Andy_${Date.now()}`;
    const insertRes = await col.insertOne({ name, age: 30, createdAt: new Date() });
    console.log("2) Insert 완료:", insertRes.insertedId.toString());

    // D) Find
    const found = await col.findOne({ _id: insertRes.insertedId });
    console.log("3) FindOne 결과:", found);

    // E) Update
    const updateRes = await col.updateOne({ _id: insertRes.insertedId }, { $set: { age: 31 } });
    console.log("4) Update 완료: matched", updateRes.matchedCount, "modified", updateRes.modifiedCount);

    // F) Find again
    const updated = await col.findOne({ _id: insertRes.insertedId });
    console.log("5) Update 후 확인:", updated);

    // G) (선택) Delete
    // const delRes = await col.deleteOne({ _id: insertRes.insertedId });
    // console.log("6) Delete 완료:", delRes.deletedCount);

  } catch (err) {
    console.error("에러:", err);
  } finally {
    await client.close();
    console.log("연결 종료");
  }
}

main();