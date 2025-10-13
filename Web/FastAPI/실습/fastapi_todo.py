#fastapi_todo
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# 요청 데이터 형식
class TodoItem(BaseModel):
    title: str
    completed: bool = False

# 임시 저장소 (DB 대신 사용)
todo_list = []

@app.get("/")
async def root():
    return {"message": "To-do API에 오신 걸 환영합니다!"}

# 전체 To-do 목록
@app.get("/todos/")
async def get_todos():
    return todo_list

# 새로운 To-do 추가
@app.post("/todos/")
async def add_todo(item: TodoItem):
    todo_id = len(todo_list)
    todo = item.dict()
    todo["id"] = todo_id
    todo_list.append(todo)
    return todo

# To-do 삭제
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    for i, todo in enumerate(todo_list):
        if todo["id"] == todo_id:
            del todo_list[i]
            return {"message": "삭제 완료"}
    raise HTTPException(status_code=404, detail="해당 ID 없음")
