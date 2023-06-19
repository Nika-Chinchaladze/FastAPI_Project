"""Module is responsible for testing following views:
all_post, one_post, create_post, delete_post, put_post.
"""

import pytest

from app import schemas


def test_all_post_view_authorized_success(authorized_client, test_posts):
    """TestCase checks that authorized user can retrieve all post data."""
    response = authorized_client.get("/posts")
    res_data = map(lambda item: schemas.SendPost(**item), response.json())
    for my_post in res_data:
        assert my_post.author.id in [1, 2]
    assert response.status_code == 200


def test_all_post_view_not_authorized_error(client, test_posts):
    """TestCase checks that not-authorized user can't retrieve
    post related information and, 401 exception error will be
    raised.
    """
    response = client.get("/posts")
    assert response.status_code == 401
    assert response.json().get("detail") == "Not authenticated"


def test_one_post_view_authorized_success(authorized_client, test_posts):
    """TestCase checks that authorized user can retrieve
    post related information based on post id.
    """
    response = authorized_client.get("/posts/1")
    res_data = schemas.SendPost(**response.json())
    assert response.status_code == 200
    assert res_data.author.id == 1
    assert res_data.title == "post 1"
    assert res_data.description == "post 1 content"
    assert res_data.price == 23.5


def test_one_post_view_authorized_non_exist_post_error(authorized_client, test_posts):
    """TestCase checks that if authorized user tries to retrieve
    information about post that doesn't exist, then 404 exception
    will be raised and special detail message will be displayed.
    """
    response = authorized_client.get("/posts/100")
    assert response.status_code == 404
    assert response.json().get("detail") == "post with id: 100, was not found!"


def test_one_post_view_not_authorized_error(client, test_posts):
    """TestCase checks that if not-authorized user tries
    to retrieve post related information, then 401 exception
    error will be raised.
    """
    response = client.get("/posts/1")
    assert response.status_code == 401
    assert response.json().get("detail") == "Not authenticated"


@pytest.mark.parametrize(
    "title, description, price",
    [
        (
            "new title",
            "new description",
            33.3,
        ),
        (
            "new title",
            "new description",
            "45.5",
        ),
    ],
)
def test_create_post_view_authorized_success(
    authorized_client, title, description, price
):
    """TestCase checks that authorized user can create new post,
    if he/she provides valid data.
    """
    post_data = {"title": title, "description": description, "price": price}
    response = authorized_client.post("/posts", json=post_data)
    res_data = schemas.SendPost(**response.json())
    assert response.status_code == 201
    assert res_data.title == post_data["title"]
    assert res_data.description == post_data["description"]
    assert res_data.price == float(post_data["price"])
    assert res_data.is_active is True
    assert res_data.author.id == 1


@pytest.mark.parametrize(
    "title, description, price",
    [
        (
            "",
            "new description",
            20,
        ),
        (
            "new title",
            "",
            20,
        ),
        (
            "",
            "",
            20,
        ),
        (
            "new title",
            "new description",
            -10,
        ),
        (
            None,
            "new description",
            20,
        ),
        (
            "new title",
            None,
            20,
        ),
        (
            "new title",
            "new description",
            None,
        ),
        (
            "new title",
            "new description",
            "string",
        ),
        (
            None,
            None,
            20,
        ),
        (
            None,
            None,
            None,
        ),
    ],
)
def test_create_post_view_authorized_wrong_data_error(
    authorized_client, title, description, price
):
    """TestCase checks that if authorized user provides invalid data,
    he/she won't be able to create new post and, 422 exception error
    will be raised.
    """
    post_data = {"title": title, "description": description, "price": price}
    response = authorized_client.post("/posts", json=post_data)
    assert response.status_code == 422


def test_create_post_view_not_authorized_error(client):
    """TestCase checks that not-authorized user can't create
    new post even he/she provides valid data and, 401 exception
    error will be raised.
    """
    post_data = {
        "title": "new post",
        "description": "by order of the tommy shelby!",
        "price": 33.3,
    }
    response = client.post("/posts", json=post_data)
    assert response.status_code == 401
    assert response.json().get("detail") == "Not authenticated"


@pytest.mark.parametrize("id", [1, 2, 3, 4])
def test_delete_post_view_authorized_success(authorized_client, test_posts, id):
    """TestCase checks that authorized user can delete his/her own posts,
    by using post id.
    """
    response = authorized_client.delete(f"/posts/{id}")
    assert response.status_code == 200
    assert response.json().get("message") == f"Post with id {id}, has been deleted!"


def test_delete_post_view_authorized_non_exist_post_error(
    authorized_client, test_posts
):
    """TestCase checks that if authorized user tries to delete the post, that
    doesn't exist then 404 exception error will be raised.
    """
    response = authorized_client.delete("/posts/100")
    assert response.status_code == 404
    assert response.json().get("detail") == "post with id: 100, was not found!"


@pytest.mark.parametrize("id", [5, 6])
def test_delete_post_view_authorized_others_post_error(
    authorized_client, test_posts, id
):
    """TestCase checks that if authorized user tries to delete another user's post,
    then 403 exception error will be raised, because user can delete only his/her
    own posts.
    """
    response = authorized_client.delete(f"/posts/{id}")
    assert response.status_code == 403
    assert (
        response.json().get("detail") == "Not authorized to perform requested action!"
    )


def test_delete_post_view_not_authorized_error(client, test_posts):
    """TestCase checks that if not-authorized user tries to delete
    post from database - 401 exception error will be raised.
    """
    response = client.delete("/posts/1")
    assert response.status_code == 401
    assert response.json().get("detail") == "Not authenticated"


@pytest.mark.parametrize("id", [1, 2, 3, 4])
def test_put_post_view_authorized_success(
    authorized_client, test_posts, update_data, id
):
    """TestCase checks that authorized user can update his/her own posts,
    by using post id.
    """
    response = authorized_client.put(f"/posts/{id}", json=update_data)
    res_data = schemas.SendPost(**response.json())
    assert response.status_code == 200
    assert res_data.title == update_data["title"]
    assert res_data.description == update_data["description"]
    assert res_data.price == update_data["price"]
    assert res_data.is_active is True
    assert res_data.author.id == 1


def test_put_post_view_authorized_non_exist_post_error(
    authorized_client, test_posts, update_data
):
    """TestCase checks that if authorized user tries to update post that
    doesn't exist then 404 exception error will be raised.
    """
    response = authorized_client.put("/posts/100", json=update_data)
    assert response.status_code == 404
    assert response.json().get("detail") == "post with id: 100, was not found!"


@pytest.mark.parametrize("id", [5, 6])
def test_put_post_view_authorized_others_post_error(
    authorized_client, test_posts, update_data, id
):
    """TestCase checks that if authorized user tries to update another user's post,
    then 403 exception error will be raised, because user can update only his/her
    posts.
    """
    response = authorized_client.put(f"/posts/{id}", json=update_data)
    assert response.status_code == 403
    assert (
        response.json().get("detail") == "Not authorized to perform requested action!"
    )


def test_put_post_view_not_authorized_error(client, test_posts, update_data):
    """TestCase checks that if not-authorized user tries to update post, then
    401 exception error will be raised.
    """
    response = client.put("/posts/1", json=update_data)
    assert response.status_code == 401
    assert response.json().get("detail") == "Not authenticated"
