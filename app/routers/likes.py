from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, oauth2, schemas
from app.database import get_db

router = APIRouter(prefix="/likes", tags=["Likes"])


@router.post("/", response_model=schemas.LikeResponse, status_code=status.HTTP_200_OK)
def like_unlike_posts(
    like: schemas.Likes,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    like_query = db.query(models.Likes).filter(
        models.Likes.post_id == like.post_id,
        models.Likes.user_id == int(current_user.id),
    )
    found_like = like_query.first()
    if found_like:
        db.delete(found_like)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="You've unliked this post",
        )
    else:
        new_like = models.Likes(post_id=like.post_id, user_id=int(current_user.id))
        db.add(new_like)
        db.commit()
        return {"message": "liked post succesfully"}
