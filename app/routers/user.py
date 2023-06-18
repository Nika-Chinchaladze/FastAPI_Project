"""Module is responsible for getting user information."""

from fastapi import status, HTTPException, Depends, APIRouter

from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from app.database import get_db


router = APIRouter(tags=["User"])


@router.get("/users/{id}", response_model=schemas.SendUser)
def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(oauth2.get_current_user),
):
    """get_user view is responsible for retrieving user specific information."""
    my_user = db.query(models.Author).filter(models.Author.id == id).first()
    # we check if user exists in the database,
    # if exists, we return user information,
    # if not exists, we raise 404 error.
    if my_user:
        return my_user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} - not exists!",
        )
