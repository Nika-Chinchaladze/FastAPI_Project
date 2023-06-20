"""Module is responsible for creating test database and,
overriding existing db instance with test_db instance for
testing purposes and creating pytest fixtures.
 """

import pytest
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.config import settings
from app.database import Base, get_db
from app.oauth2 import create_access_token
from app import models


SQLALCHEMY_DATABASE_URL = settings.database_url_test

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def get_db_test():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = get_db_test
    yield TestClient(app)


@pytest.fixture
def test_user(client) -> dict:
    user_data = {"username": "nata", "email": "fighter@gmail.com", "password": "nadira"}
    response = client.post("/register", json=user_data)
    return {"response": response.json(), "status_code": response.status_code, "id": 1}


@pytest.fixture
def test_second_user(client) -> dict:
    user_data = {"username": "nika", "email": "chincho@gmail.com", "password": "nadira"}
    response = client.post("/register", json=user_data)
    return {"response": response.json(), "status_code": response.status_code, "id": 2}


@pytest.fixture
def token(test_user):
    return create_access_token(data={"author_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


@pytest.fixture
def test_posts(test_user, session, test_second_user) -> None:
    session.add_all(
        [
            models.Post(
                title="post 1",
                description="post 1 content",
                price=23.5,
                author_id=test_user["id"],
            ),
            models.Post(
                title="post 2",
                description="post 2 content",
                price=24.5,
                author_id=test_user["id"],
            ),
            models.Post(
                title="post 3",
                description="post 3 content",
                price=25.5,
                author_id=test_user["id"],
            ),
            models.Post(
                title="post 4",
                description="post 4 content",
                price=26.5,
                author_id=test_user["id"],
            ),
            models.Post(
                title="another post 1",
                description="another post 1 content",
                price=27.5,
                author_id=test_second_user["id"],
            ),
            models.Post(
                title="another post 2",
                description="another post 2 content",
                price=28.5,
                author_id=test_second_user["id"],
            ),
        ]
    )
    session.commit()
    return None


@pytest.fixture
def update_data():
    new_data = {
        "title": "update title",
        "description": "update description",
        "price": 100,
    }
    return new_data


@pytest.fixture
def new_comment():
    data = {"comment": "This comment is from Tommy Shelby!"}
    return data


@pytest.fixture
def test_comments(test_posts, session) -> None:
    session.add_all(
        [
            models.Comment(
                comment="First User's - First Comment", author_id=1, post_id=1
            ),
            models.Comment(
                comment="First User's - Second Comment", author_id=1, post_id=1
            ),
            models.Comment(
                comment="Second User's - First Comment", author_id=2, post_id=1
            ),
        ]
    )
    session.commit()
    return None
