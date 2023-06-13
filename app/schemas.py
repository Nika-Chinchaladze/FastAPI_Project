from pydantic import BaseModel, EmailStr
from typing import Optional


# Token Data Pydantic Model
class TokenData(BaseModel):
    author_id: Optional[str] = None


# User Pydantic Models
class BaseUser(BaseModel):
    username: str
    email: EmailStr


class GetUser(BaseUser):
    password: str


class SendUser(BaseUser):
    id: int

    class Config:
        orm_mode = True
