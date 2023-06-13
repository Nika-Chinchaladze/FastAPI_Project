"""Module is responsible for creating pydantic models."""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# Token data related pydantic model.
class TokenData(BaseModel):
    id: Optional[str] = None


# User token related pydantic model.
class UserToken(BaseModel):
    access_token: str
    token_type: str


# User related pydantic models.
class BaseUser(BaseModel):
    username: str
    email: EmailStr


class GetUser(BaseUser):
    password: str


class SendUser(BaseUser):
    id: int

    class Config:
        orm_mode = True


# Post related pydantic models.
class BasePost(BaseModel):
    title: str
    description: str
    price: float
    is_active: bool = True


class GetPost(BasePost):
    pass


class SendPost(BasePost):
    created_at: datetime
    updated_at: datetime
    author: SendUser

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: SendPost
    votes: int

    class Config:
        orm_mode = True


# Comment related pydantic models.
class BaseComment(BaseModel):
    comment: str


class GetComment(BaseComment):
    id: int
    pass


class SendComment(BaseComment):
    created_at: datetime
    author: SendUser

    class Config:
        orm_mode = True