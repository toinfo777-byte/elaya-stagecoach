from __future__ import annotations

import json
import re
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # токен бота
    bot_token: str = Field(validation_alias="BOT_TOKEN")

    # БД
    db_url: str = Field(default="sqlite:////data/db.sqlite", validation_alias="DB_URL")

    # админы
    admin_ids: List[int] = Field(default_factory=list, validation_alias="ADMIN_IDS")
    admin_alert_chat_id: Optional[int] = Field(default=None, validation_alias="ADMIN_ALERT_CHAT_ID")

    # прочие опции (если используешь)
    channel_username: Optional[str] = Field(default=None, validation_alias="CHANNEL_USERNAME")
    coach_rate_sec: int = Field(default=5, validation_alias="COACH_RATE_SEC")
    coach_ttl_min: int = Field(default=60, validation_alias="COACH_TTL_MIN")
    env: str = Field(default="staging", validation_alias="ENV")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def _parse_admin_ids(cls, v):
        """
        Поддерживаем 3 варианта:
        - список уже как Python-структура
        - JSON-массив: "[1,2,3]"
        - CSV/пробелы: "1,2,3" или "1 2 3"
        """
        if v is None or v == "":
            return []
        if isinstance(v, list):
            return [int(x) for x in v]
        if isinstance(v, str):
            s = v.strip()
            # пробуем как JSON
            if s.startswith("["):
                try:
                    data = json.loads(s)
                    return [int(x) for x in data]
                except Exception:
                    pass
            # иначе парсим CSV/пробелы
            parts = re.split(r"[,\s]+", s)
            return [int(p) for p in parts if p]
        return v


settings = Settings()
