const { MongoClient, ServerApiVersion } = require("mongodb");

const uri = "mongodb+srv://ryp1662_db_user:DW8wGcXrDr69cDzm@cluster0.hlm47pc.mongodb.net/?appName=Cluster0";

async function main() {
  const client = new MongoClient(uri, { serverApi: ServerApiVersion.v1 });
  try {
    await client.connect();                // 1) 연결
    await client.db("admin").command({ ping: 1 });  // 2) ping
    console.log("Pinged your deployment. You successfully connected to MongoDB!");
  } finally {
    await client.close();
  }
}

main().catch(console.error);

