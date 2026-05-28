from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    APP_NAME: str = "Inventory Control API"
    APP_ENV: str = "development"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql+psycopg://inventory:inventory@localhost:5432/inventory_db"
    SECRET_KEY: str = Field(default="change-this-secret-key", min_length=16)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()


settings = get_settings()
