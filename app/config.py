from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Настройки веб-ядра Элайи.
    Читает переменные из корневого .env.
    """

    tg_bot_token: str
    webhook_secret: str
    base_url: str

    core_api_token: str
    guard_key: str | None = None
    env: str = "dev"
    mode: str = "local"

    model_config = SettingsConfigDict(
        env_file=".env",   # корневой .env в репозитории
        extra="ignore",    # игнорируем лишние (если вдруг появятся)
    )


settings = Settings()
