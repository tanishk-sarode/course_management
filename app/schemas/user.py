from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

from app.common.enums import RoleEnum


# ---------- Base ----------
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: RoleEnum


# ---------- Create ----------
class UserCreate(UserBase):
    password: str = Field(min_length=8) 
    # hashed_password: str


# ---------- Read ----------
class UserRead(UserBase):
    id: int
    role: RoleEnum
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Update ----------
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None


# ---------- Auth ----------
class UserLogin(BaseModel):
    email: EmailStr
    password: str
