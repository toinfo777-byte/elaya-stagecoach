# app/config.py
from __future__ import annotations

import json
from typing import List, Optional

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
    )

    # ── базовые
    bot_token: str = Field(..., alias="BOT_TOKEN")
    db_url: str = Field("sqlite:////data/db.sqlite", alias="DB_URL")
    env: str = Field("prod", alias="ENV")

    # ── админы/уведомления
    admin_alert_chat_id: Optional[int] = Field(None, alias="ADMIN_ALERT_CHAT_ID")
    # Читаем из окружения КАК СТРОКУ, а ниже превратим в список
    admin_ids_raw: str = Field("", alias="ADMIN_IDS")

    # ─
