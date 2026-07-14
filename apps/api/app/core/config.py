"""Konfiguratsiya — Pydantic Settings."""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ===== App =====
    APP_NAME: str = "AnonymousMatch"
    APP_ENV: str = Field(default="development", pattern="^(development|staging|production)$")
    APP_DEBUG: bool = False
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"
    WEBAPP_URL: str = "http://localhost:3000"
    CORS_ORIGINS: List[str] = ["*"]

    # ===== Bot =====
    BOT_TOKEN: str = ""
    BOT_USERNAME: str = "AnonymousMatchBot"
    BOT_WEBHOOK_URL: str = ""
    BOT_WEBHOOK_SECRET: str = ""

    # ===== Database =====
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "kryzen"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "anonymous_match"
    DATABASE_URL: str = ""

    @property
    def db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def db_url_sync(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # ===== Redis =====
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_URL: str = ""

    @property
    def redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # ===== Security =====
    JWT_SECRET: str = "change-me-to-a-long-random-secret-string"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TTL_HOURS: int = 720  # 30 days
    COOKIE_SECRET: str = "change-me-too"
    CSRF_SECRET: str = "change-me-csrf"
    BCRYPT_ROUNDS: int = 12

    # ===== Admin =====
    ADMIN_TELEGRAM_IDS: str = ""

    @property
    def admin_ids(self) -> List[int]:
        return [int(x.strip()) for x in self.ADMIN_TELEGRAM_IDS.split(",") if x.strip()]

    # ===== Storage =====
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    CLOUDINARY_URL: str = ""
    MEDIA_DIR: str = "/app/media"
    MAX_UPLOAD_SIZE_MB: int = 10

    # ===== Premium =====
    PREMIUM_PRICE_STARS: int = 500
    SUPERLIKE_DAILY_FREE: int = 1
    LIKES_DAILY_FREE: int = 50
    BOOST_DURATION_MINUTES: int = 30
    PREMIUM_DURATION_DAYS: int = 30

    # ===== Match =====
    SWIPE_DAILY_LIMIT: int = 100
    SUPERLIKE_WEEKLY_LIMIT: int = 5

    # ===== Rate Limit =====
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    FLOOD_WINDOW_SECONDS: int = 10
    FLOOD_MAX_MESSAGES: int = 5

    # ===== Logging =====
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = ""

    # ===== Sentry =====
    SENTRY_DSN: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
