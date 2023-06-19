"""Module is responsible for testing -> create_comment and get_comments views."""

import pytest

from app import schemas


def test_create_comment_view_authorized_success(
    authorized_client, test_posts, new_comment
):
    """TestCase checks that authorized user can add new comment under chosen post.
    The post is chosen by its id.
    """
    response = authorized_client.post("/posts/1/comments", json=new_comment)
    res_data = schemas.SendComment(**response.json())
    assert response.status_code == 201
    assert res_data.comment == new_comment["comment"]
    assert res_data.author.id == 1


def test_create_comment_view_authorized_non_exist_post_error(
    authorized_client, test_posts, new_comment
):
    """TestCase checks that if authorized user tries to add new comment under the post,
    that doesn't exist then 404 exception error will be raised and special message
    will be displayed.
    """
    response = authorized_client.post("/posts/100/comments", json=new_comment)
    assert response.status_code == 404
    assert response.json().get("detail") == "Post with id 100 not exists"


@pytest.mark.parametrize("comment", ["", None])
def test_create_comment_view_authorized_empty_string_error(
    authorized_client, test_posts, comment
):
    """TestCase checks that if authorized user tries to add new comment,
    that contains invalid data then 422 exception error will be raised.
    """
    comment_data = {"comment": comment}
    response = authorized_client.post("/posts/1/comments", json=comment_data)
    assert response.status_code == 422


def test_create_comment_view_not_authorized_error(client, test_posts, new_comment):
    """TestCase checks that is not-authorized user tries to add new comment,
    then 401 exception error will be raised and special warning message will
    be displayed.
    """
    response = client.post("/posts/1/comments", json=new_comment)
    assert response.status_code == 401
    assert response.json().get("detail") == "Not authenticated"


def test_get_comments_view_authorized_success(
    authorized_client, test_posts, test_comments
):
    """TestCase checks that authorized user can retrieve comment information,
    under specific post, that can be chosen by post id.
    """
    response = authorized_client.get("/posts/1/comments")
    res_data = map(lambda item: schemas.SendComment(**item), response.json())
    for my_comment in res_data:
        assert my_comment.author.id in [1, 2]
    assert response.status_code == 200


def test_get_comments_view_authorized_non_exist_post_error(
    authorized_client, test_posts, test_comments
):
    """TestCase checks that if authorized user tries to retrieve comment information
    under the post that doesn't exist then 404 exception error will be raised and
    special warning message will be displayed.
    """
    response = authorized_client.get("/posts/100/comments")
    assert response.status_code == 404
    assert response.json().get("detail") == "Post with id 100 not exists"


def test_get_comments_view_not_authorized_error(client, test_posts, test_comments):
    """TestCase checks that if not-authorized user tries to retrieve comment
    information under some chosen post, there will be raised 401 exception
    error with special warning message that only authenticated users can
    access these data.
    """
    response = client.get("/posts/1/comments")
    assert response.status_code == 401
    assert response.json().get("detail") == "Not authenticated"
