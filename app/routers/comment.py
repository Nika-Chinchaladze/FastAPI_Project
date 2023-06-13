from fastapi import status, HTTPException, Depends, APIRouter
from typing import List

from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/posts", tags=["Comment"])


@router.post(
    "/{id}/comments",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.SendComment,
)
def create_comment(
    id: int,
    comment_data: schemas.GetComment,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(oauth2.get_current_user),
):
    # check if chosen post exists
    chosen_post = db.query(models.Post).filter(models.Post.id == id).first()
    if chosen_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not exists",
        )
    # add new comment to chosen post
    new_comment = models.Comment(
        comment=comment_data.comment, author_id=current_user_id, post_id=id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@router.get("/{id}/comments", response_model=List[schemas.SendComment])
def get_comments(
    id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(oauth2.get_current_user),
):
    # check if chosen post exists
    chosen_post = db.query(models.Post).filter(models.Post.id == id).first()
    if chosen_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not exists",
        )

    # return post results
    post_comments = db.query(models.Comment).filter(models.Comment.post_id == id).all()
    return post_comments
