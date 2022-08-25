import pytest
from app import models


@pytest.fixture
def add_vote(test_posts, session, test_user):
    vote = models.Votes(post_id=test_posts[2].id, user_id=test_user['id'])
    session.add(vote)
    session.commit()


def test_vote_on_post(authorized_client, test_posts):
    res = authorized_client.post("/vote/", json={
        "post_id": test_posts[0].id,
        "dir": 1
    })
    
    assert res.status_code == 201


def test_vote_on_post_twice(authorized_client, test_posts, add_vote):
    res = authorized_client.post("/vote/", json={
        "post_id": test_posts[2].id,
        "dir": 1
    })
    
    assert res.status_code == 409


def test_vote_delete(authorized_client, test_posts, add_vote):
    res = authorized_client.post("/vote/", json={
        "post_id": test_posts[2].id,
        "dir": 0
    })
    
    assert res.status_code == 201


def test_vote_delete_not_exist(authorized_client, test_posts):
    res = authorized_client.post("/vote/", json={
        "post_id": test_posts[0].id,
        "dir": 0
    })
    
    assert res.status_code == 404


def test_vote_on_post_not_exist(authorized_client, test_posts):
    res = authorized_client.post("/vote/", json={
        "post_id": 10000000000,
        "dir": 1
    })
    
    assert res.status_code == 404


def test_vote_unauthorized(client, test_posts):
    res = client.post("/vote/", json={
        "post_id": test_posts[0].id,
        "dir": 1
    })
    
    assert res.status_code == 401