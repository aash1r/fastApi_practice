from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class UserOut(BaseModel):
    email: EmailStr
    id: int
    created_at: datetime
    phone_number: str

    class Config:
        from_attributes = True


class PostResponse(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut
    pass

    class Config:
        from_attributes = True


class PostOut(BaseModel):
    Post: PostResponse
    likes: int


class UserBase(BaseModel):
    email: EmailStr
    password: str
    phone_number: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Likes(BaseModel):
    post_id: int


class LikeResponse(BaseModel):
    message: str
