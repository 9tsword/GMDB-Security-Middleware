from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.db.models import RoleEnum


class UserBase(BaseModel):
    username: str
    full_name: Optional[str]
    role: RoleEnum
    is_active: bool = True


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str]
    password: str = Field(..., min_length=8)
    role: RoleEnum = RoleEnum.OPERATOR


class UserUpdate(BaseModel):
    full_name: Optional[str]
    password: Optional[str]
    role: Optional[RoleEnum]
    is_active: Optional[bool]


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
