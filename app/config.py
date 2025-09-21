from __future__ import annotations

from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    # токен бота
    bot_token: str = Field(..., env="BOT_TOKEN")

    # строка подключения к БД
    db_url: str = Field("sqlite:////data/db.sqlite", env="DB_URL")

    # прочее (опционально)
    admin_ids: str = Field("", env="ADMIN_IDS")
    admin_alert_chat_id: Optional[int] = Field(None, env="ADMIN_ALERT_CHAT_ID")
    channel_username: Optional[str] = Field(None, env="CHANNEL_USERNAME")
    env: str = Field("staging", env="ENV")

    # удобный доступ к admin_ids в виде списка int
    @property
    def admin_ids_list(self) -> List[int]:
        raw = (self.admin_ids or "").replace(" ", "")
        return [int(x) for x in raw.split(",") if x]

    class Config:
        # pydantic v1 совместимость
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
