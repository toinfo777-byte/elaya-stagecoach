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

    # админка/уведомления
    admin_alert_chat_id: Optional[int] = Field(None, alias="ADMIN_ALERT_CHAT_ID")
    # читаем как строку (поддержим JSON и “через запятую”)
    admin_ids_raw: Optional[str] = Field("", alias="ADMIN_IDS")

    # опциональные
    channel_username: Optional[str] = Field(None, alias="CHANNEL_USERNAME")
    coach_rate_sec: int = Field(2, alias="COACH_RATE_SEC")
    coach_ttl_min: int = Field(30, alias="COACH_TTL_MIN")

    @computed_field
    @property
    def admin_ids(self) -> List[int]:
        """
