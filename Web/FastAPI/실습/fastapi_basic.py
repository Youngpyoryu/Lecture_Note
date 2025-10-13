from fastapi import FastAPI
from pydantic import BaseModel
import asyncio

app = FastAPI()

#데이터 모델 정의(요청 본문)
class Item(BaseModel):
    name : str
    price : float

@app.get("/") #기본 엔드포인트
async def root():
    return {"message" : "FastAPI에 오신 것을 환영합니다."}

items = [] #아이템 저장소 추가
from uuid import uuid4 #POST에 아이템 ID를 부여&저장

@app.post("/items/") #POST 요청 처리(자동 문서화+검증)
async def create_item(item:Item):
    item_dict = item.dict()
    item_dict["id"] = str(uuid4()) # UUID 형식의 고유 ID추가
    items.append(item_dict)
    await asyncio.sleep(1)
    return {"message" : "아이템이 저장되었습니다.", "item":item_dict}
@app.get("/items/")
async def get_all_items():
    return items
@app.delete("/items/{item_id}")
async def delete_items(item_id : str):
    global items
    for item in items:
        if item["id"] == item_id:
            items.append(item)
            return {"message" : f"{item_id} 삭제 완료"}
    return {"error" : "해당 ID의 아이템 없음."}

@app.get("/wait/{seconds}") #path parameter+비동기 처리
async def wait(seconds:int):
    await asyncio.sleep(seconds)
    return {"message" : f"{seconds}초 기다렸어요."}