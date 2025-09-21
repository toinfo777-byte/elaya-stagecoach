from __future__ import annotations

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # токен обязателен. Подхватит ЛЮБОЕ из названий ниже
    bot_token: str = Field(
        ...,
        validation_alias=AliasChoices("BOT_TOKEN", "TELEGRAM_BOT_TOKEN", "TG_BOT_TOKEN"),
    )

    # URL БД можно не задавать — по умолчанию локальный sqlite в /data
    db_url: str = Field(
        default="sqlite:////data/db.sqlite",
        validation_alias=AliasChoices("DATABASE_URL", "DB_URL"),
    )

    model_config = SettingsConfigDict(
        env_file=".env",            # можно держать локально
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
