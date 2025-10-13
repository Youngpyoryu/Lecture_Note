# fastapi_post.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# 요청 본문 형식 정의
class Item(BaseModel):
    name: str
    price: float
    is_on_sale: bool = False

# POST 요청 처리
@app.post("/items/")
async def create_item(item: Item):
    return {
        "message": "Item received!",
        "name": item.name,
        "price": item.price,
        "on_sale": item.is_on_sale
    }

# 테스트용 GET
@app.get("/")
async def root():
    return {"message": "Hello FastAPI!"}

