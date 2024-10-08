from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def createUsers(user: schemas.UserBase, db: Session = Depends(get_db)):
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    newUser = models.User(**user.model_dump())
    db.add(newUser)
    db.commit()
    db.refresh(newUser)
    return newUser


@router.get("/{id}", response_model=schemas.UserOut)
def get_users(id: int, db: Session = Depends(get_db)):
    new_user = db.query(models.User).filter(models.User.id == id).first()
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with the id: {id} not found!",
        )
    return new_user


@router.delete("/")
def delete_users(db: Session = Depends(get_db)):
    users = db.query(models.User).delete()
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Users already deleted"
        )
    db.commit()
    return None
