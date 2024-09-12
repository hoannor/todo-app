from pydantic import BaseModel


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

    class Config:
        orm_mode = True
