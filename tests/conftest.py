import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.config import settings
from app.database import get_db, Base
from app.oauth2 import create_access_token
from app import models


SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def overrid_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = overrid_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email":"test@t.com", "password":"12345"}
    res = client.post("/users/", json=user_data)
    new_user = res.json()
    new_user["password"] = user_data["password"]
    assert res.status_code == 201
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


@pytest.fixture
def test_posts(test_user, session,):
    posts_data = [
        {
            "title": "first title",
            "content": "first content",
            "owner_id": test_user['id'],
        },
        {
            "title": "second title",
            "content": "second content",
            "owner_id": test_user['id'],
        },
        {
            "title": "3rd title",
            "content": "3rd content",
            "owner_id": test_user['id'],
        }
    ]
    def create_post_model(post):
        return models.Post(**post)

    post_map = list(map(create_post_model, posts_data))
    session.add_all(post_map)
    session.commit()
    posts = session.query(models.Post).all()
    return posts
    