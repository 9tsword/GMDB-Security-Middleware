from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core.security import get_password_hash
from app.db import models
from app.db.session import get_db
from app.schemas import user as user_schemas

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", response_model=user_schemas.UserOut)
def create_user(
    payload: user_schemas.UserCreate,
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN)),
    db: Session = Depends(get_db),
):
    if db.query(models.User).filter(models.User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    user = models.User(
        username=payload.username,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=List[user_schemas.UserOut])
def list_users(
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN)),
    db: Session = Depends(get_db),
):
    return db.query(models.User).all()


@router.put("/{user_id}", response_model=user_schemas.UserOut)
def update_user(
    user_id: int,
    payload: user_schemas.UserUpdate,
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN)),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.password:
        user.hashed_password = get_password_hash(payload.password)
    if payload.role:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN)),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}
