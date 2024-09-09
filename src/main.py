from typing import List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, Session

app = FastAPI()
# tao URL de co the ket noi den database
DATABASE_URL = "postgresql+psycopg2://postgres:1234@localhost:5433/todoapp"

# tao 1 engine de ket noi den PostgreSQL
engine = create_engine(DATABASE_URL)

#tao base cho cac model (tao cac table)
Base = declarative_base()

# model todoItem
class todoItem(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key = True)
    title = Column(String, nullable = False)
    description = Column(String)
    completed = Column(Boolean, default = False)

# tao bang trong co so du lieu (sao ham nay khong goi y)
Base.metadata.create_all(engine)

# tao 1 Session de lam viec voi co so du lieu
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

#dependency de lay session tu co so du lieu
def get_db():
     db = SessionLocal()
     try:
         yield db
     finally:
         db.close()

# Dinh nghia Pydantic model de dung lam response model
class todoItemResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool = False

    class Config:
        orm_mode = True

#note: chuyen tat cac cac du lieu tra ve (response_model cua cac end-point thanh kieu du lieu todoItemResponse thuoc kieu base model de co the tra ve duoi dang JSON cho trang web)
# End-point 1: lay du lieu tu tat ca cac to-do
@app.get("/todos", response_model = List[todoItemResponse])
async def get_todos():
    session = SessionLocal()
    # truy van du lieu tu bang
    todos = session.query(todoItem).all()
    session.close()
    return todos

# End-point 2: them 1 to-do moi
@app.post("/todos", response_model = todoItemResponse)
async def create_todo(todo: todoItem):
    session = SessionLocal()
    tg = todoItem(title = todo.title, description = todo.description, completed = todo.completed)
    session.add(tg)
    session.commit()
    session.close()
    #return ra mot bien todoItemResponse
    return todoItemResponse(
        id =
        title = todo.title
        description = todo.description
        completed = todo.completed
    )

# End-point 3: xoa 1 to-do theo id cua chung
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    session = SessionLocal()
    todo_to_delete = session.query(todoItem).filter(todoItem.id == todo_id).first()
    if todo_to_delete is not None:
        session.delete(todo_to_delete)
        session.commit()
        session.close()
        return {"message": "todo has been deleted!"}
    else:
        session.close()
        raise HTTPException(status_code = 404, detail = "todo not found")

# End-point 4: thanh doi trang thai completed cua 1 to-do
@app.patch("/todos/{todo_id}", response_model = todoItemResponse)
async def update_todo(todo_id: int):
    session = SessionLocal()
    todo_to_update = session.query(todoItem).filter(todoItem.id == todo_id).first()
    if todo_to_update is None:
        session.close()
        raise HTTPException(status_code = 404, detail = "todo not found!")
    todo_to_update['completed'] = not todo_to_update['completed']
    session.commit()
    session.close()
    return {"message": "todo has been update"}



