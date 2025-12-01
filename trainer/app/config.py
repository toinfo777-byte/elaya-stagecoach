from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Единственное обязательное поле: токен бота
    tg_bot_token: str = Field(..., alias="TG_BOT_TOKEN")

    # Остальное сейчас не обязательно
    base_url: str | None = None

    model_config = SettingsConfigDict(
        # Ищем .env и в trainer/.env, и в корне ../.env
        env_file=(".env", "../.env"),
        extra="ignore",
        populate_by_name=True,
    )


settings = Settings()
