import json
from typing import List
from urllib import response
from app import schemas
import pytest


# def test_get_posts(authorized_client, test_posts):
def test_get_posts(client, test_posts):
    res = client.get("/posts/")
    # def validate(post):
    #     return schemas.PostOut(**post)
    # posts_list = list(map(validate, res.json())) 
    
    assert len(res.json()) == len(test_posts)
    assert res.status_code == 200


def test_unauthorized_user_get_one_post(client, test_posts):
    res = client.get(f"posts/{test_posts[0].id}")
    assert res.status_code == 401


def test_user_get_one_post_not_exist(authorized_client, test_posts):
    res = authorized_client.get("posts/10000000000000000")
    assert res.status_code == 404


def test_user_get_one_post(authorized_client, test_posts):
    res = authorized_client.get(f"posts/{test_posts[0].id}")
    post = schemas.PostOut(**res.json())
    assert post.Post.id == test_posts[0].id
    assert post.Post.content == test_posts[0].content
    assert post.Post.title == test_posts[0].title


@pytest.mark.parametrize("title, content, published", [
    ("new title", "new content", True),
    ("new title2", "new content2", False),
    ("new title3", "new content3", True),
])
def test_user_create_post(authorized_client, test_user, test_posts, title, content, published):
    res = authorized_client.post("/posts/create_posts", json={
        "title": title,
        "content": content,
        "published": published
    })
    post = schemas.PostResponse(**res.json())
    assert res.status_code == 201
    assert post.title == title
    assert post.content == content
    assert post.published == published
    assert post.owner_id == test_user['id']


def test_user_create_post_default_published(authorized_client, test_user):
    res = authorized_client.post("/posts/create_posts", json={
        "title": "some",
        "content": "some"
    })
    post = schemas.PostResponse(**res.json())
    assert res.status_code == 201
    assert post.title == "some"
    assert post.content == "some"
    assert post.published == True
    assert post.owner_id == test_user['id']



def test_unauthorized_user_create_post(client):
    res = client.post("/posts/create_posts", json={
        "title": "some",
        "content": "some"
    })
    assert res.status_code == 401


def test_unauthorized_user_delete_post(client, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


def test_user_delete_post(authorized_client, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 204


def test_user_delete_post_not_exist(authorized_client):
    res = authorized_client.delete("/posts/100000000")
    assert res.status_code == 404


def test_update_post(authorized_client, test_posts, test_user):
    data = {
        "title": "Updateted",
        "content": "updated",
        "id": test_posts[0].id
    }
    res = authorized_client.put(f"posts/{test_posts[0].id}", json=data)
    updated_post = schemas.PostResponse(**res.json())
    assert res.status_code == 200


def test_unauthorized_user_update_post(client, test_posts):
    res = client.put(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


def test_user_update_post_not_exist(authorized_client, test_posts):
    data = {
        "title": "Updateted",
        "content": "updated",
        "id": test_posts[0].id
    }
    res = authorized_client.put("/posts/100000000", json=data)
    assert res.status_code == 404