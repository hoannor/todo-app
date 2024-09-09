from typing import List
from fastapi import FastAPI, HTTPException, Request
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
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

    id = Column(Integer, primary_key = True, nullable = False)
    title = Column(String, nullable = False)
    description = Column(String)
    completed = Column(Boolean, default = False)
    inprogress = Column(Boolean, default = False)

# tao bang trong co so du lieu
Base.metadata.create_all(engine)

# tao 1 Session de lam viec voi co so du lieu
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

# Dinh nghia Pydnatic model de dung lam input model
class todoItemInput(BaseModel):
    title: str
    description: str = None
    completed: bool = False
    inprogress: bool = False

# Dinh nghia Pydantic model de dung lam response model
class todoItemResponse(BaseModel):
    id: int
    title: str
    description: str = None
    completed: bool = False
    inprogress: bool = False

    class Config:
        orm_mode = True

#note: chuyen tat cac cac du lieu tra ve (response_model cua cac end-point thanh kieu du lieu todoItemResponse thuoc kieu base model de co the tra ve duoi dang JSON cho trang web)

# # End-point 0: trang chu
# @app.get("/")
# def root():
#     return {"message": "Hello World"}

# End-point 1: lay du lieu tu tat ca cac to-do
@app.get("/todos", response_model = List[todoItemResponse])
async def get_todos():
    session = SessionLocal()
    # truy van du lieu tu bang
    todos = session.query(todoItem).all()
    return todos

# End-point 2: them 1 to-do moi
@app.post("/todos", response_model = todoItemResponse)
async def create_todo(todo: todoItemInput):
    session = SessionLocal()
    tg = todoItem(title = todo.title, description = todo.description, completed = todo.completed, inprogress = todo.inprogress)
    session.add(tg)
    session.commit()
    session.refresh(tg)
    return tg

# End-point 3: xoa 1 to-do theo id cua chung
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    session = SessionLocal()
    todo_to_delete = session.query(todoItem).filter(todoItem.id == todo_id).first()
    if todo_to_delete is not None:
        session.delete(todo_to_delete)
        session.commit()
        return {"message": "todo has been deleted!"}
    else:
        raise HTTPException(status_code = 404, detail = "todo not found")

# End-point 4: thanh doi trang thai completed cua 1 to-do
@app.patch("/todos/completed/{todo_id}", response_model = todoItemResponse)
async def update_todo_completed(todo_id: int):
    session = SessionLocal()
    todo_to_update = session.query(todoItem).filter(todoItem.id == todo_id).first()
    if todo_to_update is None:
        raise HTTPException(status_code = 404, detail = "todo not found!")
    todo_to_update.completed = not todo_to_update.completed
    session.commit()
    session.refresh(todo_to_update)
    return todo_to_update

# End-point 5: danh dau 1 todo la dang trong qua trinh lam
@app.patch("/todos/in_progress/{todo_id}", response_model = todoItemResponse)
async def update_todo_in_progress(todo_id: int):
    session = SessionLocal()
    todo_to_update = session.query(todoItem).filter(todoItem.id == todo_id).first()
    if todo_to_update is None:
        raise HTTPException(status_code = 404, detail = "todo not found!")
    todo_to_update.in_progress = not todo_to_update.inprogress
    session.commit()
    session.refresh(todo_to_update)
    return todo_to_update

# End-point 6: chuc nang xoa cac todo da hoan thanh
@app.patch("/todos/deletedones")
async def delete_dones():
    session = SessionLocal()
    todo_to_delete = session.query(todoItem).filter(todoItem.completed == True).first()
    while todo_to_delete is not None:
        session.delete(todo_to_delete)
        session.commit()
        todo_to_delete = session.query(todoItem).filter(todoItem.completed == True).first()
    return {"message": "All dones have been deleted"}

