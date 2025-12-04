from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # pydantic-settings v2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",          # лишние переменные просто игнорируем
    )

    SAFE_MODE: bool = False
    SENTRY_DSN: str | None = None
    SQLITE_PATH: str = "stagecoach.db"
    GUARD_KEY: str | None = None

    # чтобы не ругался, если вдруг захочешь читать эти поля из ядра
    ENV: str = "dev"
    MODE: str = "local"
    LOG_LEVEL: str = "INFO"


settings = Settings()
