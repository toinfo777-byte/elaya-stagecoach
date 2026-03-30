from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    tg_bot_token: str = ""
    trainer_core_url: str = ""
    trainer_guard_key: str = ""

    env: str = "dev"
    mode: str = "dev"


settings = Settings()