from __future__ import annotations

from typing import Set

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Бот и окружение
    bot_token: str = Field(..., alias="BOT_TOKEN")
    env: str = Field("prod", alias="ENV")

    # База данных
    db_url: str = Field("sqlite:////data/db.sqlite", alias="DB_URL")

    # Админы и сервисные параметры (всё опционально)
    admin_alert_chat_id: int | None = Field(None, alias="ADMIN_ALERT_CHAT_ID")
    admin_ids: Set[int] = Field(default_factory=set, alias="ADMIN_IDS")
    channel_username: str | None = Field(None, alias="CHANNEL_USERNAME")
    coach_rate_sec: int = Field(0, alias="COACH_RATE_SEC")
    coach_ttl_min: int = Field(0, alias="COACH_TTL_MIN")
    lim_api_key: str | None = Field(None, alias="LIM_API_KEY")

    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_file=".env",      # локально можно держать .env
        env_prefix="",        # читаем переменные как есть (BOT_TOKEN, DB_URL, ...)
        extra="ignore",       # игнорировать лишние переменные окружения
    )

    # ADMIN_IDS можно задавать "123,456" — распарсим в set[int]
    @field_validator("admin_ids", mode="before")
    @classmethod
    def _parse_admin_ids(cls, v):
        if v in (None, "", []):
            return set()
        if isinstance(v, (set, list, tuple)):
            return {int(x) for x in v}
        if isinstance(v, str):
            return {int(x) for x in v.replace(" ", "").split(",") if x}
        return {int(v)}


# Глобальный инстанс настроек
settings = Settings()
