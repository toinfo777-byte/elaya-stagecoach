# app/config.py
from __future__ import annotations

import json
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # .env не обязателен, но пусть будет; пустые значения игнорируем
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
    )

    # ── основные настройки
    bot_token: str = Field(..., alias="BOT_TOKEN")
    db_url: str = Field("sqlite:////data/db.sqlite", alias="DB_URL")
    env: str = Field("prod", alias="ENV")

    # ── админы/уведомления
    admin_alert_chat_id: Optional[int] = Field(None, alias="ADMIN_ALERT_CHAT_ID")
    admin_ids: List[int] = Field(default_factory=list, alias="ADMIN_IDS")

    # ── опционально (есть в окружении)
    channel_username: Optional[str] = Field(None, alias="CHANNEL_USERNAME")
    coach_rate_sec: int = Field(2, alias="COACH_RATE_SEC")
    coach_ttl_min: int = Field(30, alias="COACH_TTL_MIN")

    # Принимаем ADMIN_IDS как JSON ([1,2]) ИЛИ как "1,2, 3"
    @field_validator("admin_ids", mode="before")
    @classmethod
    def _parse_admin_ids(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, (list, tuple, set)):
            return [int(x) for x in v]
        if isinstance(v, str):
            s = v.strip()
            # JSON-массив
            if s.startswith("[") and s.endswith("]"):
                try:
                    arr = json.loads(s)
                    return [int(x) for x in arr]
                except Exception:
                    pass
            # Строка с разделителями: запятая/пробел/точка с запятой
            parts = [p for p in s.replace(";", ",").replace(" ", ",").split(",") if p]
            return [int(p) for p in parts]
        raise TypeError("ADMIN_IDS must be JSON array or comma-separated string")


settings = Settings()
