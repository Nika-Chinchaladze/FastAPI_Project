"""Module is responsible for creating pydantic models."""

from pydantic import BaseModel, EmailStr, validator, ValidationError
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

    @validator("username")
    def username_must_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValidationError("username can't be empty!")
        return value


class GetUser(BaseUser):
    password: str

    @validator("password")
    def password_must_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValidationError("password can't be empty!")
        return value


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

    @validator("title")
    def title_must_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValidationError("Title can't be empty!")
        return value

    @validator("description")
    def description_must_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValidationError("Description can't be empty!")
        return value

    @validator("price")
    def price_must_not_be_negative(cls, value):
        if value is None or value < 0:
            raise ValidationError("Price can't be negative number!")
        return value


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

    @validator("comment")
    def comment_must_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValidationError("Comment can't be empty!")
        return value


class GetComment(BaseComment):
    pass


class SendComment(BaseComment):
    created_at: datetime
    author: SendUser

    class Config:
        orm_mode = True


# User logout related pydantic model
class UserLogout(BaseModel):
    username: str
    password: str
