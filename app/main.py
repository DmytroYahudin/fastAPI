from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
import time

from . import models
from .database import engine
from .routers import post, user

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(post.router)
app.include_router(user.router)


@app.get("/")
def index():
    return {"message": "Hello Dima!"}
