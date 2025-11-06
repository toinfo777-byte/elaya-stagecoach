# app/config.py
from __future__ import annotations

import os
from pydantic import Field
from pydantic_settings import BaseSettings  # <-- новая правильная импорт-точка


class Settings(BaseSettings):
    env: str = Field(default=os.getenv("ENV", "staging"))
    build_mark: str = Field(default=os.getenv("BUILD_MARK", "manual"))

    bot_profile: str = Field(default=os.getenv("BOT_PROFILE", "hq"))

    admin_alert_chat_id: int | None = Field(
        default=None,
        description="ID админ-чата (отрицательное значение для групп).",
    )

    alert_dedup_window_sec: int = Field(
        default=int(os.getenv("ALERT_DEDUP_WINDOW_SEC", "15"))
    )

    disable_tg: bool = Field(default=os.getenv("DISABLE_TG", "0") == "1")

    class Config:
        env_prefix = ""


settings = Settings()
