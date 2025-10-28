# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str | None = None
    TG_BOT_TOKEN: str | None = None

    MODE: str = "polling"
    ENV: str = "dev"

    BUILD_SHA: str | None = None
    SENTRY_DSN: str | None = None
    STATUS_KEY: str | None = None
    STATUS_DIR: str | None = None
    TZ_DEFAULT: str | None = "Europe/Moscow"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
