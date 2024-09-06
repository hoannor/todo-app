from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from database import get_cursor


app = FastAPI()

# dang loi chua sua
templates = Jinja2Templates(directory = "templates") # nghien cuu cac render cua thu vien nay

# tao 1 model pydantic cho to-do item
class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool = False

cursor = get_cursor()

# End-point 0: khoi tao 1 bang moi
create_table_querry = '''
CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    completed BOOLEAN DEFAULT FALSE
)
'''
cursor.execute(create_table_querry)
cursor.close()

# su dung async de co the tranh bi bat dong bo gay mat du lieu loi chuong trinh cho cac ham truy cap du lieu tu co so du lieu

# trang chu cua he thong
@app.get("/", response_class = HTMLResponse)
async def home_screen(request: Request):
    # render trang home_screen cho trang chu
    return templates.TemplateResponse("home_screen.html", {"request": request})


# End-point 1: lay danh sach tat ca cac to-do
@app.get("/todos", response_model = List[TodoItem]) # response_model de gioi han kieu du lieu tra ve cua ham def
async def get_todos():
    cursor = get_cursor()
    cursor.execute('''SELECT * FROM todos''')
    todos = cursor.fetchall() # lay toan bo cac hang sau khi truy van
    return todos

# End-point 2: them 1 to-do moi
@app.post("/todos", response_model = TodoItem)
async def create_todo(todo: TodoItem):
    cursor = get_cursor()
    cursor.execute(
        '''
        INSERT INTO todos (title, description, completed)
        VALUES (%s, %s, %s) RETURNING id
        ''',
        (todo.title, todo.description, todo.completed)
    )
    new_id = cursor.fetchone()["id"]
    return {**todo.dict(), "id": new_id} #ham aict su dung de lay thu tu tu dien trong db cua hang de lam id cho hang do (1 doi tuong to-do)

# End-point 3: xoa 1 to-do theo id
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    cursor = get_cursor()
    cursor.execute('''DELETE FROM todos WHERE id = %s''', (todo_id,))
    if cursor.rowcount == 0: # kiem tra xem hang do co phai la hang 0 khong vi neu la hang 0 thi khong con du lieu do co the xoa
        raise HTTPException(status_code = 404, detail = "todo not found!") # tra ve loi 404 khi khong the tim thay duoc dia chi
    return {"message": "todo has been deleted!"}

# End-point 4: thay doi trang thai completed cua 1 to-do
@app.patch("/todos/{todo_id}", response_model = TodoItem) # ham patch de cap nhap 1 phan cua du lieu con cac phan khac cua du lieu duoc du nguyen
async def update_todo(todo_id: int):
    cursor = get_cursor()
    # print("hello there")
    # kiem tra xem to-do co ton tai trong bang khong
    cursor.execute(
        '''
        SELECT * FROM todos WHERE id = %s
        ''',
        (todo_id,)
    )
    todo = cursor.fetchone()

    if todo is None:
        raise HTTPException(status_code = 404, detail = "To-do not found!")

    # tao 1 bien moi luu trang thai nghich dao cua completed hien tai
    new_completed_status = not todo['completed']

    # cap nhat lat trang thai moi vao co su du lieu
    cursor.execute(
        '''
        UPDATE todos
        SET completed = %s
        WHERE id = %s
        RETURNING id, title, description, completed
        ''',
        (new_completed_status, todo_id)
    )

    update_todo = cursor.fetchone()
    if update_todo is None:
        raise HTTPException(status_code = 404, detail = "Can not update to-do!")

    return {"message": "to-do had been update!"}

cursor.close()