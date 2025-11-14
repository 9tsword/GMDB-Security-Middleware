from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.router import api_router
from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db import models
from app.db.models import RoleEnum
from app.db.session import Base, SessionLocal, engine

settings = get_settings()

app = FastAPI(title=settings.app_name)
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        _ensure_default_admin(session)
        _seed_defaults(session)


@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


def _ensure_default_admin(session: Session) -> None:
    if not session.query(models.User).filter(models.User.username == settings.initial_admin_username).first():
        admin = models.User(
            username=settings.initial_admin_username,
            full_name="系统管理员",
            hashed_password=get_password_hash(settings.initial_admin_password),
            role=RoleEnum.ADMIN,
        )
        session.add(admin)
        session.commit()


def _seed_defaults(session: Session) -> None:
    defaults = {
        "default_concurrency": "4",
        "default_batch_size": "500",
        "log_retention_days": "30",
        "default_algorithm": "SM4",
        "key_version": "v1",
        "key_valid_until": datetime.utcnow().replace(year=datetime.utcnow().year + 1).isoformat(),
        "key_last_rotation": datetime.utcnow().isoformat(),
    }
    for key, value in defaults.items():
        config = session.query(models.SystemConfiguration).filter(models.SystemConfiguration.key == key).first()
        if not config:
            config = models.SystemConfiguration(key=key, value=value)
            session.add(config)
    if not session.query(models.HelpDocument).first():
        session.add(
            models.HelpDocument(
                title="中间件管理界面使用指南",
                category="guide",
                content="欢迎使用 GMDB 加密中间件管理平台。本指南涵盖敏感字段配置、迁移任务监控、系统设置等内容。",
                attachment_url=None,
            )
        )
    session.commit()
