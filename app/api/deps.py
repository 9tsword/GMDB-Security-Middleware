from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_username
from app.db import models
from app.db.session import get_db


def get_current_user(
    token: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> models.User:
    if token is None or not token.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    raw_token = token.split()[1]
    username = get_current_username(raw_token)
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    return user


def require_role(*roles: models.RoleEnum):
    def role_checker(user: models.User = Depends(get_current_user)) -> models.User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return role_checker


async def ensure_admin(user: models.User = Depends(require_role(models.RoleEnum.ADMIN))):
    return user
