"""Module is responsible for post's comment feature."""

from fastapi import status, HTTPException, Depends, APIRouter
from typing import List

from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from app.database import get_db


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
    """create_comment view is responsible for adding
    new comments to existing posts in the database.
    user must be logged in to execute this operation.
    """
    # we check if chosen post exists and
    # if post not exists we raise 404 error
    chosen_post = db.query(models.Post).filter(models.Post.id == id).first()
    if chosen_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not exists",
        )
    # if post exists than user can add comment on it.
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
    """get_comments view is responsible for returning post
    specific comments, user must be logged in to execute
    this operation.
    """
    # we check if chosen post exists,
    # if post not exists then we raise 404 error.
    chosen_post = db.query(models.Post).filter(models.Post.id == id).first()
    if chosen_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not exists",
        )

    # if post exists then we return every comment,
    # related to this chosen post.
    post_comments = db.query(models.Comment).filter(models.Comment.post_id == id).all()
    return post_comments
