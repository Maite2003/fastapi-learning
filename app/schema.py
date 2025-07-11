import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

"""
pydantic
you create a class that is use as a model of what the user
should send on a post request. The class should extend BaseModel
It is use to validate the info the user sends, so for a post a user has to
send a title which is going to be a string and content which has to be
a string also.

schema made with pydantic.
used as a model for what user can send in requests
"""

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(UserCreate):
    pass

class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime.datetime

    """ So that it can convert sqlalchemy models into pydantic models"""
    model_config = ConfigDict(from_attributes=True)

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    owner_id: int
    owner: UserOut
    created_at: datetime.datetime

    """ So that it can convert sqlalchemy models into pydantic models"""
    model_config = ConfigDict(from_attributes=True)

class PostOut(BaseModel):
    post: Post
    votes: int = 0


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int | None = None

class Vote(BaseModel):
    post_id: int
    dir: int = Field(ge = 0, le = 1)
