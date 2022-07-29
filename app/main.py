from turtle import title
from typing import Optional
from fastapi import Depends, FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi",
            user="postgres",
            password="12345",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("Database connected seccesfully!")
        break
    except Exception as error:
        print("Connection to database failed")
        print(f"Error: {error}")
        time.sleep(2)


@app.get("/")
def index():
    return {"message": "Hello Dima!"}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.post("/create_posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).one_or_none()
    if post:
        return {"post detail": post}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    chosen_post = db.query(models.Post).filter(models.Post.id == id)

    if chosen_post.one_or_none():
        chosen_post.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"post id: {id} was not found"
        )


@app.put("/posts/{id}")
def update_posts(id: int, post: Post, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    chosen_post = post_query.one_or_none()

    if chosen_post:
        post_query.update(post.dict(), synchronize_session=False)
        db.commit()
        return {"data": post_query.first()}
        
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"post id: {id} was not found"
        )
