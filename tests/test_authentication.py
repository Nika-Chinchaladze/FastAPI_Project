"""Module is responsible for testing register, login and logout endpoints."""

import pytest
from jose import jwt
from datetime import datetime, timedelta

from app import schemas, models
from app.config import settings


def test_register_view_success(test_user):
    """TestCase checks register view, if it creates new author
    and returns token for another authorized operations.
    """
    res_data = schemas.UserToken(**test_user["response"])
    decode_token = jwt.decode(
        token=res_data.access_token,
        key=settings.secret_key,
        algorithms=[settings.algorithm],
    )
    assert test_user["status_code"] == 201
    assert decode_token["author_id"] == 1
    assert res_data.token_type == "bearer"


def test_register_view_user_already_exists_error(test_user, client):
    """TestCase checks that already registered author,
    can't be registered second time and, 409 exception
    should be raised.
    """
    author_data = {
        "username": "nata",
        "email": "fighter@gmail.com",
        "password": "nadira",
    }
    response = client.post("/register", json=author_data)
    assert response.status_code == 409


@pytest.mark.parametrize(
    "username, email, password",
    [
        ("", "fighter@gmail.com", "nadira"),
        ("tommy", "fighter@gmail.com", ""),
        (None, "fighter@gmail.com", "nadira"),
        ("tommy", "fighter@gmail.com", None),
    ],
)
def test_register_view_empty_string_error(client, username, email, password):
    """TestCase checks that author won't be able to register
    with invalid credentials and, 422 exception error will be raised.
    """
    author_data = {"username": username, "email": email, "password": password}
    response = client.post("/register", json=author_data)
    assert response.status_code == 422


def test_login_view_success(client, test_user):
    """TestCase checks that already registered author will
    be able to log in with valid credentials and, get
    token for another authorized operations.
    """
    author_info = {"username": "nata", "password": "nadira"}
    response = client.post("/login", data=author_info)
    res_data = schemas.UserToken(**response.json())
    decode_token = jwt.decode(
        token=res_data.access_token,
        key=settings.secret_key,
        algorithms=[settings.algorithm],
    )
    assert response.status_code == 200
    assert decode_token["author_id"] == 1
    assert res_data.token_type == "bearer"


@pytest.mark.parametrize(
    "username, password, status_code",
    [
        ("wrong", "nadira", 403),
        ("nata", "wrong", 403),
        ("wrong", "wrong", 403),
        (None, "nadira", 422),
        ("nata", None, 422),
        (None, None, 422),
        ("", "nadira", 422),
        ("nata", "", 422),
        ("", "", 422),
    ],
)
def test_login_view_wrong_credentials_error(
    client, test_user, username, password, status_code
):
    """TestCase checks that user can't log in by using invalid credentials and,
    token won't be generated for him/her.
    """
    author_info = {"username": username, "password": password}
    response = client.post("/login", data=author_info)
    assert response.status_code == status_code


def test_logout_view_authorized_success(authorized_client):
    """TestCase checks that authorized user will be able to call logout endpoint
    and, get special message that he/she was logged out successfully.
    """
    response = authorized_client.get("/logout")
    assert response.status_code == 200
    assert response.json().get("message") == "You have been logged out successfully!"


def test_logout_view_non_authorized_error(client):
    """TestCase checks that only authorized user will be able to
    access logout endpoint and not-authorized user won't and, 401
    exception error will be raised.
    """
    response = client.get("/logout")
    assert response.status_code == 401
    assert response.json().get("detail") == "Not authenticated"


def test_logout_view_save_blacklist_token(authorized_client, test_user, session):
    """TestCase checks that if authorized user access logout endpoint,
    then his/her token will be stored into black_list table and, user
    will no longer be able to use it.
    """
    response = authorized_client.get("/logout")
    black_token = test_user["response"]["access_token"]
    db_data = (
        session.query(models.BlackList)
        .filter(models.BlackList.token == black_token)
        .first()
    )
    assert response.status_code == 200
    assert db_data is not None


def test_logout_view_remove_old_blacklist_tokens(authorized_client, test_user, session):
    """TestCase checks that when authorized user access logout endpoint,
    then in the background there will be executed special function that
    remove old(older than 30 minutes) tokens from black_list table.
    """
    old_token = (
        "my_randomly_generated_token_which_is_to_old_and_needs_to_be_removed_from_db"
    )
    old_record = models.BlackList(
        token=old_token, user_id=1, created_at=datetime.now() - timedelta(minutes=50)
    )
    session.add(old_record)
    session.commit()
    # call logout endpoint, that should remove old tokens from db
    response = authorized_client.get("/logout")
    db_data = (
        session.query(models.BlackList)
        .filter(models.BlackList.token == old_token)
        .first()
    )
    assert response.status_code == 200
    assert db_data is None
