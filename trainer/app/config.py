# trainer/app/config.py
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Конфиг для pydantic-settings v2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",          # лишние переменные окружения просто игнорируем
    )

    # Telegram
    tg_bot_token: str = ""  # без токена

    # Связь с ядром (Stagecoach Web)
    trainer_core_url: str = ""
    trainer_guard_key: str = ""

    # Прочее
    env: str = "dev"
    mode: str = "dev"


settings = Settings()
