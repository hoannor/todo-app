from pydantic import BaseModel

class UserCreate(BaseModel):
    user_name: str
    password: str

class UserResponse(BaseModel):
    id: int
    user_name: str
    password: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TodoItemInput(BaseModel):
    title: str
    description: str = None
    completed: bool = False
    inprogress: bool = False

class TodoItemResponse(BaseModel):
    id: int
    title: str
    description: str = None
    completed: bool = False
    inprogress: bool = False
    user_id: int

    class Config:
        orm_mode = True

