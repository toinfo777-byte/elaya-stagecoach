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

    # базовые
    bot_token: str = Field(..., alias="BOT_TOKEN")
    db_url: str = Field("sqlite:////data/db.sqlite", alias="DB_URL")
    env: str = Field("prod", alias="ENV")

    # админы/уведомления
    admin_alert_chat_id: Optional[int] = Field(None, alias="ADMIN_ALERT_CHAT_ID")
    admin_ids_raw: Optional[str] = Field("", alias="ADMIN_IDS")  # строка из ENV

    # опциональные
    channel_username: Optional[str] = Field(None, alias="CHANNEL_USERNAME")
    coach_rate_sec: int = Field(2, alias="COACH_RATE_SEC")
    coach_ttl_min: int = Field(30, alias="COACH_TTL_MIN")

    # HTTP (FastAPI) — выключен по умолчанию для воркера
    http_enabled: bool = Field(False, alias="HTTP_ENABLED")

    @computed_field
    @property
    def admin_ids(self) -> List[int]:
        s = (self.admin_ids_raw or "").strip()
        if not s:
            return []
        # JSON: "[1,2,3]"
        if s.startswith("[") and s.endswith("]"):
            try:
                return [int(x) for x in json.loads(s)]
            except Exception:
                pass
        # "1,2,3" / "1 2 3" / "1;2;3"
        parts = [p for p in s.replace(";", ",").replace(" ", ",").split(",") if p]
        if parts:
            return [int(p) for p in parts]
        # одно значение
        try:
            return [int(s)]
        except Exception:
            return []


settings = Settings()
__all__ = ["Settings", "settings"]
