"""Module is responsible for user authentication."""

from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from app import models, schemas, utils, oauth2, crud
from app.database import get_db


router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.UserToken)
def login(
    author_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """login view checks if user exists in the database
    and if he/she exists than logs him/her into program
    and gives newly generated token for executing another
    operations.
    """
    # here we check if user exists in the database.
    my_author = (
        db.query(models.Author)
        .filter(models.Author.username == author_credentials.username)
        .first()
    )

    # if user doesn't exist than we throw 403 error.
    if my_author is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Wrong Credentials!"
        )

    # if user exists then we check if password is correct
    # if password is incorrect than we throw 403 error
    if not utils.verify_user_password(
        plain_password=author_credentials.password, hashed_password=my_author.password
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Wrong Credentials!"
        )
    else:
        # if credentials are correct, we generate and provide JWT Token to user
        payload_data = {"author_id": my_author.id}
        access_token = oauth2.create_access_token(data=payload_data)
        return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(author_credentials: schemas.GetUser, db: Session = Depends(get_db)):
    """register view checks if user exists in the database
    and if he/she not exists than registers him/her into program
    and gives newly generated token for executing another
    operations.
    """
    # here we check if user exists in the database.
    my_author = (
        db.query(models.Author)
        .filter(models.Author.username == author_credentials.username)
        .first()
    )
    # if user not exists then we register him/her.
    if my_author is None:
        # we have to hash user password.
        hashed_password = utils.hash_user_password(author_credentials.password)
        author_credentials.password = hashed_password
        # user data is already renewed with hashed password.
        new_user = models.Author(**author_credentials.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        # now we can access created users credentials.
        created_author = (
            db.query(models.Author)
            .filter(models.Author.email == author_credentials.email)
            .first()
        )
        # we generate JWT Token for user.
        payload_data = {"author_id": created_author.id}
        access_token = oauth2.create_access_token(data=payload_data)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        # if user already exists than we raise 208 error with
        # message that user is already registered.
        raise HTTPException(
            status_code=status.HTTP_208_ALREADY_REPORTED,
            detail=f"User with name {my_author.username} - already exists!",
        )


@router.get("/logout", status_code=status.HTTP_200_OK)
def logout(
    user_token: str = Depends(oauth2.oauth_schema),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(oauth2.get_current_user),
):
    """logout view is responsible for logging out users,
    user must be logged in to access this endpoint, and
    after executing logout view, user token will be added
    into black list, so user needs to generate another token
    to access some login_required data, also logout view cleans
    database from old tokens.
    """
    # we check database and remove old black list tokens.
    crud.remove_old_black_tokens(db)
    # we add logged-out user's token into blacklist table.
    if crud.save_in_black_list(user_token=user_token, user_id=current_user_id, db=db):
        return {"message": "You have been logged out successfully!"}
