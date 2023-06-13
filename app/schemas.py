from pydantic import BaseModel
from typing import Optional


class TokenData(BaseModel):
    author_id: Optional[str] = None
