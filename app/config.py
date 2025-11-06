from __future__ import annotations
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # базовые
    env: str = Field(default="staging", alias="ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    bot_profile: str = Field(default="hq", alias="BOT_PROFILE")

    # токены
    tg_bot_token: Optional[str] = Field(default=None, alias="TELEGRAM_TOKEN")
    bot_token: Optional[str] = Field(default=None, alias="BOT_TOKEN")

    # админ-уведомления
    admin_alert_chat_id: Optional[int] = Field(default=None, alias="ADMIN_ALERT_CHAT_ID")
    alert_dedup_window_sec: int = Field(default=15, alias="ALERT_DEDUP_WINDOW_SEC")

    # вебхук (дефолтный путь теперь жестко в роутере, но оставим на будущее)
    webhook_base: Optional[str] = Field(default=None, alias="WEBHOOK_BASE")
    webhook_secret: Optional[str] = Field(default=None, alias="WEBHOOK_SECRET")

    # рендер/сборка (для статусов)
    build_mark: Optional[str] = Field(default=None, alias="BUILD_MARK")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",           # лишние переменные не падают
        case_sensitive=False,
    )


settings = Settings()
