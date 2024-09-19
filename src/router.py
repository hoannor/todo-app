from datetime import timedelta
from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.auth import get_password_hash, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, \
    get_current_user, ADMIN_SECRET
from src.models import TodoItem, User
from src.schemas import TodoItemResponse, TodoItemInput, UserCreate, Token, UserResponse
from src.service import get_db

router = APIRouter()


                        #_____authen/author router_____

# End-point: dang ki nguoi dung
@router.post("/register", response_model = UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_name == user.user_name).first()
    if db_user:
        raise HTTPException(status_code = 400, detail = "Username already registed")
    hashed_password = get_password_hash(user.password)
    if user.admin_password == ADMIN_SECRET:
        new_user = User(user_name = user.user_name, hashed_password = hashed_password, is_admin = True)
    else:
        new_user = User(user_name = user.user_name, hashed_password = hashed_password, is_admin = False)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponse(id = new_user.id,
                      user_name = new_user.user_name,
                      password = new_user.hashed_password,
                      is_admin = new_user.is_admin)

# End-point dang nhap va lay JWT token
@router.post("/token", response_model = Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Incorrect username or password", headers = {"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data = {"sub": user.user_name}, expires_delta = access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}



                           # _____todos router_____

@router.get("/todos", response_model = List[TodoItemResponse])
async def get_todos(db: Session = Depends(get_db)):
    todos = db.query(TodoItem).all()
    return todos

@router.post("/todos", response_model = TodoItemResponse)
async def create_todo(todo: TodoItemInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tg = TodoItem(title = todo.title, description = todo.description, completed = todo.completed, inprogress = todo.inprogress, user_id = current_user.id)
    db.add(tg)
    db.commit()
    db.refresh(tg)
    return TodoItemResponse(
        id = tg.id,
        title = tg.title,
        description = tg.description,
        completed = tg.completed,
        inprogress = tg.inprogress,
        user_id = tg.user_id
    )


@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.is_admin is True:
        todo_to_delete = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
        if todo_to_delete is not None:
            db.delete(todo_to_delete)
            db.commit()
            return {"message": "todo has been deleted"}
        else:
            raise HTTPException(status_code = 404, detail = "todo not found")
    else:
        todo_to_delete = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
        if todo_to_delete is not None:
            if current_user.id == todo_to_delete.user_id:
                db.delete(todo_to_delete)
                db.commit()
                return {"message": "todo has been deleted"}
            else:
                raise HTTPException(status_code=401, detail="you don't have permission to do that!")
        else:
            raise HTTPException(status_code = 404, detail = "todo not found")

@router.patch("/todos/completed/{todo_id}", response_model = TodoItemResponse)
async def update_todo_completed(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo_to_update = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if todo_to_update is None:
        raise HTTPException(status_code = 404, detail = "todo not found")
    if current_user.is_admin is True:
        todo_to_update.completed = not todo_to_update.completed
        db.commit()
        db.refresh(todo_to_update)
        return todo_to_update
    else:
        raise HTTPException(status_code = 401, detail = "you don't have permission to do that!")

@router.patch("/todos/in_progress/{todo_id}", response_model = TodoItemResponse)
async def update_todo_in_progress(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo_to_update = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if todo_to_update is None:
        raise HTTPException(status_code = 404, detail = "todo not found")
    if current_user.is_admin is True:
        todo_to_update.inprogress = not todo_to_update.inprogress
        db.commit()
        db.refresh(todo_to_update)
        return todo_to_update
    else:
        raise HTTPException(status_code = 401, detail = "you don't have permission to do that!")

@router.delete("/todos_delete_done/delete_dones")
async def delete_dones(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.is_admin is True:
        db.query(TodoItem).filter(TodoItem.completed == True).delete(synchronize_session='fetch')
        db.commit()
        return {"message": "All dones have been deleted"}
    raise HTTPException(status_code = 401, detail = "you don't have permission to do that!")
