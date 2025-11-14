from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = Field(default="GMDB Security Middleware")
    secret_key: str = Field(default="change-this-secret")
    access_token_expire_minutes: int = Field(default=60)
    database_url: str = Field(default="sqlite:///./gmdb_middleware.db")
    initial_admin_username: str = Field(default="admin")
    initial_admin_password: str = Field(default="ChangeMe123!")

    class Config:
        env_prefix = "GMDB_"
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
