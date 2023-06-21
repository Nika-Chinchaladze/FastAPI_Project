"""Module is responsible for post related CRUD operation."""

from fastapi import status, HTTPException, Depends, APIRouter
from typing import List

from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from app.database import get_db, engine

models.Base.metadata.create_all(bind=engine)


router = APIRouter(prefix="/posts", tags=["Post"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.SendPost])
def all_post(
    db: Session = Depends(get_db),
    current_user_id: object = Depends(oauth2.get_current_user),
):
    """all_post view is responsible for retrieving all posts from database,
    user must be logged in to execute this operation.
    """
    my_posts = db.query(models.Post).all()
    return my_posts


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.SendPost)
def one_post(
    id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(oauth2.get_current_user),
):
    """one_post view is responsible for retrieving
    information about one specific post.
    user must be logged in to execute this operation.
    """
    my_post = db.query(models.Post).filter(models.Post.id == id).first()
    # we check if chosen post exists, if not exists
    # we raise 404 error, but if exists then we return
    # desired information.
    if my_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id}, was not found!",
        )
    return my_post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.SendPost)
def create_post(
    new_post: schemas.GetPost,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(oauth2.get_current_user),
):
    """create_post module is responsible for creating new posts,
    user must be logged in to execute this operation.
    """
    my_post = models.Post(author_id=current_user_id, **new_post.dict())
    db.add(my_post)
    db.commit()
    db.refresh(my_post)
    return my_post


@router.delete("/{id}")
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(oauth2.get_current_user),
):
    """delete_post view is responsible for deleting chosen post
    from database, user must be logged in to execute this operation.
    """
    my_query = db.query(models.Post).filter(models.Post.id == id)
    my_post = my_query.first()
    # we check if chosen post exists in the database.
    if my_post:
        # we check if chosen post belongs to current user.
        if my_post.author_id == current_user_id:
            my_query.delete()
            db.commit()
            return {"message": f"Post with id {id}, has been deleted!"}
        else:
            # if chosen post doesn't belong to current user, then
            # he/she won't be able to delete it, because we raise
            # 403 error.
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform requested action!",
            )
    else:
        # if chosen post not exists, then we will raise 404 error.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id}, was not found!",
        )


@router.put("/{id}", response_model=schemas.SendPost)
def put_post(
    id: int,
    update_post: schemas.GetPost,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(oauth2.get_current_user),
):
    """put_post view is responsible for updating existing post
    in the database, user must be logged in to execute this operation.
    """
    my_query = db.query(models.Post).filter(models.Post.id == id)
    my_post = my_query.first()
    # we check if chosen post exists in the database.
    if my_post:
        # we check if chosen post belongs to current user.
        if my_post.author_id == current_user_id:
            my_query.update(update_post.dict(), synchronize_session=False)
            db.commit()
            db.refresh(my_post)
            return my_post
        else:
            # if chosen post doesn't belong to current user, then we will
            # raise 403 error and he/she won't be able to modify it.
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform requested action!",
            )
    else:
        # if chosen post not exists in the database, then we will
        # raise 404 error.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id}, was not found!",
        )
