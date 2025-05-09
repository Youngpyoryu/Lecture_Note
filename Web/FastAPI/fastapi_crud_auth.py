from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

#  DB 설정
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "users_todos.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

#  DB 모델
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, nullable=False)

#  Pydantic 모델
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TodoCreate(BaseModel):
    title: str
    completed: bool = False

#  FastAPI 앱
app = FastAPI()
Base.metadata.create_all(bind=engine)

# DB 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#  회원가입
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다.")
    new_user = User(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    return {"message": "회원가입 완료", "user_id": new_user.id}

#  로그인
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        User.username == user.username, User.password == user.password).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="로그인 실패")
    return {"message": "로그인 성공", "user_id": db_user.id}

#  To-do 생성
@app.post("/users/{user_id}/todos")
def create_todo(user_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    new_todo = Todo(title=todo.title, completed=todo.completed, owner_id=user_id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

#  To-do 조회
@app.get("/users/{user_id}/todos")
def get_user_todos(user_id: int, db: Session = Depends(get_db)):
    return db.query(Todo).filter(Todo.owner_id == user_id).all()

#  To-do 삭제
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="할 일을 찾을 수 없음")
    db.delete(todo)
    db.commit()
    return {"message": "삭제 완료"}
