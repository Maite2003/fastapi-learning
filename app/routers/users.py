
from .. import schema
from .. import utils
from app import models, utils
from ..database import SessionDep

from typing import List
from fastapi import status, HTTPException, APIRouter
from sqlalchemy import select

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.UserOut)
def create_user(user: schema.UserCreate, db: SessionDep): # type: ignore

    # Hash the password
    user.password = utils.hash(user.password)
    
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=List[schema.UserOut])
def get_users(db: SessionDep): # type: ignore
    users_query = select(models.User)
    users = db.scalars(users_query)
    return users

@router.get("/{id}", response_model=schema.UserOut)
def get_user(id: int, db: SessionDep): # type: ignore
    user_query = select(models.User).where(models.User.id == id)
    user = db.scalar(user_query)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} does not exists")
    
    return user
