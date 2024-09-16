from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    password: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class todoItemInput(BaseModel):
    title: str
    description: str = None
    completed: bool = False
    inprogress: bool = False

class todoItemResponse(BaseModel):
    id: int
    title: str
    description: str = None
    completed: bool = False
    inprogress: bool = False
    user_id: int

    class Config:
        orm_mode = True

