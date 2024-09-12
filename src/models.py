from sqlalchemy import Column, String, Integer, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:1234@localhost:5433/todoapp"

engine = create_engine(DATABASE_URL)

Base = declarative_base()

class todoItem(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key = True, nullable = False)
    title = Column(String, nullable = False)
    description = Column(String)
    completed = Column(Boolean, default = False)
    inprogress = Column(Boolean, default = False)

Base.metadata.create_all(engine)

