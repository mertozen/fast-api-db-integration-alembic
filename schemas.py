from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class ItemBase(BaseModel):
    content: str


class ItemCreate(ItemBase):
    pass


class ItemOut(ItemBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
