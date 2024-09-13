from datetime import timedelta
from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.auth import get_password_hash, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user
from src.models import todoItem, User
from src.schemas import todoItemResponse, todoItemInput, UserCreate, Token
from src.service import get_db

router = APIRouter()


                        #_____authen/author router_____

# End-point: dang ki nguoi dung
@router.post("/register", response_model = UserCreate)
def register_user(user: UserCreate, db: Session = Depends(get_db())):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code = 400, detail = "Username already registed")
    hashed_password = get_password_hash(user.password)
    new_user = User(username = user.username, hashed_password = hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# End-point dang nhap va lay JWT token
@router.post("/token", response_model = Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db())):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Incorrect username or password", headers = {"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data = {"sub": user.username}, expires_delta = access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
                           # _____todos router_____

@router.get("/todos", response_model = List[todoItemResponse])
async def get_todos(db: Session = Depends(get_db)):
    todos = db.query(todoItem).all()
    return todos

@router.post("/todos", response_model = todoItemResponse)
async def create_todo(todo: todoItemInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user())):
    tg = todoItem(title = todo.title, description = todo.description, completed = todo.completed, inprogress = todo.inprogress, user_id = current_user.id)
    db.add(tg)
    db.commit()
    db.refresh(tg)
    return tg

@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo_to_delete = db.query(todoItem).filter(todoItem.id == todo_id).first()
    if todo_to_delete is not None:
        db.delete(todo_to_delete)
        db.commit()
        return {"message": "todo has been deleted"}
    else:
        raise HTTPException(status_code = 404, detail = "todo not found")

@router.patch("/todos/completed/{todo_id}", response_model = todoItemResponse)
async def update_todo_completed(todo_id: int, db: Session = Depends(get_db)):
    todo_to_update = db.query(todoItem).filter(todoItem.id == todo_id).first()
    if todo_to_update is None:
        raise HTTPException(status_code = 404, detail = "todo not found")
    todo_to_update.completed = not todo_to_update.completed
    db.commit()
    db.refresh(todo_to_update)
    return todo_to_update

@router.patch("/todos/in_progress/{todo_id}", response_model = todoItemResponse)
async def update_todo_in_progress(todo_id: int, db: Session = Depends(get_db)):
    todo_to_update = db.query(todoItem).filter(todoItem.id == todo_id).first()
    if todo_to_update is None:
        raise HTTPException(status_code = 404, detail = "todo not found")
    todo_to_update.inprogress = not todo_to_update.inprogress
    db.commit()
    db.refresh(todo_to_update)
    return todo_to_update

@router.delete("/todos_delete_done/delete_dones")
async def delete_dones(db: Session = Depends(get_db)):
    todo_to_delete = db.query(todoItem).filter(todoItem.completed == True).first()
    while todo_to_delete is not None:
        db.delete(todo_to_delete)
        db.commit()
        todo_to_delete = db.query(todoItem).filter(todoItem.completed == True).first()
    return {"message": "All dones have been deleted"}