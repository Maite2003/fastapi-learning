from .config import settings
from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

class Base(DeclarativeBase):
    pass

SQLMODEL_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'
engine = create_engine(SQLMODEL_DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, bind=engine)

def get_session():
    with SessionLocal() as session:
        yield session

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

SessionDep = Annotated[SessionLocal, Depends(get_session)]
