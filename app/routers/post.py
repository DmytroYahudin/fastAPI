from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from .. import models, oauth2, schemas
from ..database import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[schemas.PostOut])
def get_posts(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    posts = (
        db.query(models.Post, func.count(models.Votes.post_id).label("votes"))
        .join(models.Votes, models.Votes.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    return posts


@router.post(
    "/create_posts",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.PostResponse,
)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    user: int = Depends(oauth2.get_current_user),
):
    new_post = models.Post(owner_id=user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(
    id: int, db: Session = Depends(get_db), user: int = Depends(oauth2.get_current_user)
):
    post = (
        db.query(models.Post, func.count(models.Votes.post_id).label("votes"))
        .join(models.Votes, models.Votes.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == id)
        .one_or_none()
    )
    if post:
        return post
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int, db: Session = Depends(get_db), user: int = Depends(oauth2.get_current_user)
):
    chosen_post = db.query(models.Post).filter(models.Post.id == id)

    if not chosen_post.one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"post id: {id} was not found"
        )

    if chosen_post.first().owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You can delete only your own posts",
        )
    else:
        chosen_post.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.PostResponse)
def update_posts(
    id: int,
    post: schemas.PostBase,
    db: Session = Depends(get_db),
    user: int = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    chosen_post = post_query.one_or_none()

    if not chosen_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"post id: {id} was not found"
        )

    if chosen_post.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You can update only your own posts",
        )
    else:
        post_query.update(post.dict(), synchronize_session=False)
        db.commit()
        return post_query.first()
