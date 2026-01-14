// db.js
require("dotenv").config();
const { MongoClient } = require("mongodb");

const uri = process.env.MONGODB_URI;
const dbName = process.env.DB_NAME;
const colName = process.env.COL_NAME;

let client;
let collection;

async function connectDB() {
  if (!uri) throw new Error("MONGODB_URI is missing in .env");

  if (collection) return collection; // 이미 연결되어 있으면 재사용

  client = new MongoClient(uri);
  await client.connect();

  // 연결 확인(ping)
  await client.db("admin").command({ ping: 1 });
  console.log("OK: MongoDB connected (ping)");

  collection = client.db(dbName).collection(colName);
  console.log(`OK: using ${dbName}.${colName}`);

  return collection;
}

async function closeDB() {
  if (client) await client.close();
}

module.exports = { connectDB, closeDB };
