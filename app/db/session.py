from sqlalchemy import create_engine

from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

SUPPORTED_BACKENDS = {"sqlite", "postgresql", "mysql", "oracle", "mssql"}

settings = get_settings()

database_url = settings.database_url
url = make_url(database_url)
backend = url.get_backend_name()

if backend not in SUPPORTED_BACKENDS:
    raise ValueError(
        f"Unsupported database backend '{backend}'. Supported backends: {', '.join(sorted(SUPPORTED_BACKENDS))}."
    )

connect_args: dict[str, object] = {}
if backend == "sqlite":
    connect_args = {"check_same_thread": False}

engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
