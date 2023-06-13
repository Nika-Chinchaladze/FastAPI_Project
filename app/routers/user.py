from fastapi import status, HTTPException, Depends, APIRouter

from sqlalchemy.orm import Session
from app import models, schemas
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

router = APIRouter(tags=["User"])


@router.get("/users/{id}", response_model=schemas.SendUser)
def get_user(id: int, db: Session = Depends(get_db)):
    my_user = db.query(models.Author).filter(models.Author.id == id).first()
    if my_user:
        return my_user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} - not exists!",
        )
