"""Module is responsible for testing get_user view."""

from app import schemas


def test_get_user_view_authorized_success(authorized_client, test_posts):
    """Testcase checks that authorized user must be able to retrieve,
    user basic information.
    """
    response = authorized_client.get("/users/1")
    res_data = schemas.SendUser(**response.json())
    assert response.status_code == 200
    assert res_data.username == "nata"
    assert res_data.email == "fighter@gmail.com"


def test_get_user_view_authorized_non_exist_error(authorized_client):
    """Testcase checks that view raises 404 exception,
    if authorized user tries get information about user,
    doesn't exist.
    """
    response = authorized_client.get("/users/100")
    assert response.status_code == 404


def test_get_user_view_unauthorized_error(client):
    """Testcase checks that not-authorized user,
    can't be able to retrieve user information,
    and 401 exception must be raised.
    """
    response = client.get("/users/1")
    assert response.status_code == 401
