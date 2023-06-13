"""Module is responsible for hashing and verifying user's password."""

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_user_password(password: str) -> str:
    """function is responsible for hashing user password."""
    return pwd_context.hash(password)


def verify_user_password(plain_password: str, hashed_password: str) -> bool:
    """function is responsible for verifying, if hashed version of user input
    password is correct.
    """
    return pwd_context.verify(plain_password, hashed_password)
