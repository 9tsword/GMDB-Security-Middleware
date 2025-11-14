
import secrets
from datetime import datetime, timedelta

from typing import Dict

from fastapi import HTTPException, status
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

_sessions: Dict[str, Dict[str, str]] = {}


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(username: str, expires_minutes: int) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
    _sessions[token] = {"username": username, "expires_at": expires_at.isoformat()}
    return token


def get_current_username(token: str) -> str:
    session = _sessions.get(token)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if datetime.fromisoformat(session["expires_at"]) < datetime.utcnow():
        del _sessions[token]
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    return session["username"]


def revoke_token(token: str) -> None:
    _sessions.pop(token, None)
