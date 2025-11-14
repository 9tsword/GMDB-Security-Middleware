from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, revoke_token, verify_password
from app.db import models
from app.db.session import get_db
from app.schemas import auth as auth_schemas

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=auth_schemas.Token)
def login(payload: auth_schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive account")

    settings = get_settings()
    expires_minutes = settings.access_token_expire_minutes
    token = create_access_token(user.username, expires_minutes)
    return auth_schemas.Token(
        access_token=token,
        expires_at=datetime.utcnow() + timedelta(minutes=expires_minutes),
    )


@router.post("/logout")
def logout(authorization: str = Header(..., alias="Authorization")):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing token")
    token = authorization.split()[1]
    revoke_token(token)
    return {"message": "Logged out"}
