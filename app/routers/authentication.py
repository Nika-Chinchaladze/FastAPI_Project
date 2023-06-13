from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from app import models, schemas, utils, oauth2
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.UserToken)
def login(
    author_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    my_author = (
        db.query(models.Author)
        .filter(models.Author.username == author_credentials.username)
        .first()
    )

    # we check is email is correct
    if my_author is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Wrong Credentials!"
        )

    # we check is password is correct
    if not utils.verify_user_password(
        plain_password=author_credentials.password, hashed_password=my_author.password
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Wrong Credentials!"
        )
    else:
        # if credentials are correct, we need to generate and provide JWT Token
        payload_data = {"author_id": my_author.id}
        access_token = oauth2.create_access_token(data=payload_data)
        return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(author_credentials: schemas.GetUser, db: Session = Depends(get_db)):
    # check if username doesn't exist
    my_author = (
        db.query(models.Author)
        .filter(models.Author.username == author_credentials.username)
        .first()
    )
    if my_author is None:
        # we have to hash user password
        hashed_password = utils.hash_user_password(author_credentials.password)
        author_credentials.password = hashed_password
        # user data is already renewed with hashed password
        new_user = models.Author(**author_credentials.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        # now we can access created users credentials
        created_author = (
            db.query(models.Author)
            .filter(models.Author.email == author_credentials.email)
            .first()
        )
        # now we have to generate JWT Token for user
        payload_data = {"author_id": created_author.id}
        access_token = oauth2.create_access_token(data=payload_data)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_208_ALREADY_REPORTED,
            detail=f"User with name {my_author.username} - already exists!",
        )
