from fastapi import status, HTTPException, Depends, APIRouter
from typing import List, Optional

from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/posts", tags=["Post"])


@router.get("/", response_model=List[schemas.SendPost])
def all_post(
    db: Session = Depends(get_db),
    current_user_id: object = Depends(oauth2.get_current_user),
    limit: Optional[int] = 4,
    skip: Optional[int] = 0,
    search: Optional[str] = "",
):
    my_posts = (
        db.query(models.Post)
        .filter(models.Post.title.contains(search))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return my_posts


@router.get("/{id}", response_model=schemas.SendPost)
def one_post(
    id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(oauth2.get_current_user),
):
    my_post = db.query(models.Post).filter(models.Post.id == id).first()
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
    my_post = models.Post(author_id=current_user_id, **new_post.dict())
    db.add(my_post)
    db.commit()
    db.refresh(my_post)
    return my_post


@router.delete("/{id}", response_model=schemas.SendPost)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(oauth2.get_current_user),
):
    my_post = db.query(models.Post).filter(models.Post.id == id).first()
    if my_post:
        if my_post.author_id == current_user_id:
            db.delete(my_post)
            db.commit()
            return my_post
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform requested action!",
            )
    else:
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
    my_query = db.query(models.Post).filter(models.Post.id == id)
    my_post = my_query.first()
    if my_post:
        if my_post.author_id == current_user_id:
            my_query.update(update_post.dict(), synchronize_session=False)
            db.commit()
            db.refresh(my_post)
            return my_post
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform requested action!",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id}, was not found!",
        )
