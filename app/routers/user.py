from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from ..utils import password_hash
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserCreateResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = password_hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{id}", response_model=schemas.UserCreateResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).one_or_none()

    if not user:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User id: {id} was not found"
        )
    
    return user