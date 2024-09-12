from http.client import responses
from typing import List

from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import todoItem, DATABASE_URL
from src.schemas import todoItemResponse, todoItemInput

app = FastAPI()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

                            # _____todos router_____

@app.get("/todos", response_model = List[todoItemResponse])
async def get_todos():
    session = SessionLocal()
    todos = session.query(todoItem).all()
    return todos

@app.post("/todos", response_model = todoItemResponse)
async def create_todo(todo: todoItemInput):
    session = SessionLocal()
    tg = todoItem(title = todo.title, description = todo.description, completed = todo.completed, inprogress = todo.inprogress)
    session.add(tg)
    session.commit()
    session.refresh(tg)
    return tg

@app.delete("/todos{todo_id}")
async def delete_todo(todo_id: int):
    session = SessionLocal()
    todo_to_delete = session.query(todoItem).filter(todoItem.id == todo_id).first()
    if todo_to_delete is not None:
        session.delete(todo_to_delete)
        session.commit()
        return {"message": "todo has been deleted"}
    else:
        raise HTTPException(status_code = 404, detail = "todo not found")

@app.patch("/todos/completed/{todo_id}", response_model = todoItemResponse)
async def update_todo_completed(todo_id: int):
    session = SessionLocal()
    todo_to_update = session.query(todoItem).filter(todoItem.id == todo_id).first()
    if todo_to_update is None:
        raise HTTPException(status_code = 404, detail = "todo not found")
    todo_to_update.completed = not todo_to_update.completed
    session.commit()
    session.refresh(todo_to_update)
    return todo_to_update

@app.patch("/todos/in_progress/{todo_id}", response_model = todoItemResponse)
async def update_todo_in_progress(todo_id: int):
    session = SessionLocal()
    todo_to_update = session.query(todoItem).filter(todoItem.id == todo_id).first()
    if todo_to_update is None:
        raise HTTPException(status_code = 404, detail = "todo not found")
    todo_to_update.inprogress = not todo_to_update.inprogress
    session.commit()
    session.refresh(todo_to_update)
    return todo_to_update

@app.delete("/todos/deletedones")
async def delete_dones():
    session = SessionLocal()
    todo_to_delete = session.query(todoItem).filter(todoItem.completed == True).first()
    while todo_to_delete is not None:
        session.delete(todo_to_delete)
        session.commit()
        todo_to_delete = session.query(todoItem).filter(todoItem.completed == True).first()
    return {"message": "All dones have been deleted"}