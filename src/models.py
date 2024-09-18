from sqlalchemy import Column, String, Integer, Boolean, column, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

from src.service import engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True, index = True)
    user_name = Column(String, unique = True, index = True, nullable = False)
    hashed_password = Column(String, nullable = False)
    is_admin = Column(Boolean, default = False)

    todos = relationship("TodoItem", back_populates = "owner")

class TodoItem(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key = True, nullable = False)
    title = Column(String, nullable = False)
    description = Column(String)
    completed = Column(Boolean, default = False)
    inprogress = Column(Boolean, default = False)
    user_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User", back_populates = "todos")

Base.metadata.create_all(engine)

