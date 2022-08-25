from app import schemas
from app.config import settings

from jose import jwt

import pytest

def test_create_user(client):
    res = client.post("/users/", json={"email": "test@t.com", "password": "12345"})
    new_user = schemas.UserCreateResponse(**res.json())
    assert res.status_code == 201
    assert new_user.email == "test@t.com"


def test_login_user(client, test_user):

    res = client.post("/login", data={"username": test_user["email"], "password": test_user["password"]})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")
    assert res.status_code == 200
    assert id == test_user["id"]
    assert login_res.token_type == "bearer"


@pytest.mark.parametrize("email, password, status_code", [
    ("test@t.com", "wrong_password", 403),
    ("testtt@t.com", "12345", 403),
    (None, "12345", 422),
    ("test@t.com", None, 422),
]) 
def test_incorrect_login(client, test_user, email, password, status_code):
    res = client.post("/login", data={"username": email, "password": password})
    assert res.status_code == status_code
