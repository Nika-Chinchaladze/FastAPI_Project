"""Module is responsible for JWT token related operations."""

from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JOSEError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from .config import settings


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth_schema = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    """function creates unique token for logged in user."""
    to_encode = data.copy()

    expire_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire_time})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(user_token: str, credential_exception):
    """function verifies if token used by user is valid."""
    try:
        decoded_jwt = jwt.decode(
            token=user_token, key=SECRET_KEY, algorithms=[ALGORITHM]
        )
        id: str = decoded_jwt.get("author_id")
        # if user tries to access some data by using invalid,
        # token, then we will raise 403 error.
        if id is None:
            raise credential_exception
        token_data = schemas.TokenData(id=id)
        return token_data
    except JOSEError:
        raise credential_exception


def get_current_user(
    user_token: str = Depends(oauth_schema), db: Session = Depends(get_db)
):
    """function returns current user's id, if user's credentials and JWT token are valid."""
    credential_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    author = verify_access_token(user_token, credential_exception)
    current_user = (
        db.query(models.Author).filter(models.Author.id == int(author.id)).first()
    )
    return current_user.id
