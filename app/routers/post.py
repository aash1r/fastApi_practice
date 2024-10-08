from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import oauth2

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=list[schemas.PostOut])
def get_posts(
    db: Session = Depends(get_db),
    user_id: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):

    posts = (
        db.query(models.Post, func.count(models.Likes.post_id).label("likes"))
        .join(models.Likes, models.Likes.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .order_by(models.Post.id)
        .filter(models.Post.title.contains(search))
        .limit(limit=limit)
        .offset(skip)
        .all()
    )

    return posts


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse
)
def create_posts(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    one_post = (
        db.query(models.Post, func.count(models.Likes.post_id).label("likes"))
        .join(models.Likes, models.Likes.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == id)
        .first()
    )
    if not one_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with the id: {id} does not exist",
        )
    return one_post


@router.put("/{id}", response_model=schemas.PostResponse)
def update_posts(
    id: int,
    new_post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} cannot be found",
        )
    if post.owner_id != int(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized to perform this action",
        )
    update_data = {
        models.Post.title: new_post.title,
        models.Post.content: new_post.content,
    }
    post_query.update(update_data, synchronize_session=False)
    db.commit()
    return post_query.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    print(f"Post owner_id: {post.owner_id}")
    print(f"Current user id: {current_user.id}")
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} cannot be found",
        )
    if post.owner_id != int(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized to perform this action",
        )
    post_query.delete(synchronize_session=False)
    db.commit()
    return None


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_allposts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).delete()
    print(posts)

    if posts is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Posts already deleted"
        )
    db.commit()
    return None
