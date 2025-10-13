from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 앱 생성
app = FastAPI()

# SQLite 설정
SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# 세션 연결
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# DB 모델
class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)

# Pydantic 모델
class TodoItem(BaseModel):
    title: str
    completed: bool = False

# DB 생성
Base.metadata.create_all(bind=engine)

# DB 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 기본 라우트
@app.get("/")
def root():
    return {"message": "To-do API with SQLite에 오신 걸 환영합니다!"}

# 전체 목록 조회
@app.get("/todos/")
def get_todos(db: Session = Depends(get_db)):
    return db.query(Todo).all()

# 할 일 추가
@app.post("/todos/")
def add_todo(item: TodoItem, db: Session = Depends(get_db)):
    todo = Todo(title=item.title, completed=item.completed)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

# 할 일 삭제
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="해당 ID 없음")
    db.delete(todo)
    db.commit()
    return {"message": "삭제 완료"}