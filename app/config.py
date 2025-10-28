# app/config.py
from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Единая точка конфигурации.
    Поддерживает и новое имя BOT_TOKEN, и старое TG_BOT_TOKEN.
    """

    # Режим работы текущего процесса: "web" | "polling" | "bot"
    MODE: str = Field(default="web")

    # Токены (любой из двух имён можно задавать в окружении)
    BOT_TOKEN: Optional[str] = None
    TG_BOT_TOKEN: Optional[str] = None  # для обратной совместимости

    # Прочие опциональные переменные (необязательно задавать)
    ENV: Optional[str] = None
    BUILD_SHA: Optional[str] = None
    LOG_LEVEL: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))
    SENTRY_DSN: Optional[str] = None

    # ваши кастомные ключи (оставлены как есть, если используются в проекте)
    STATUS_DIR: Optional[str] = None
    STATUS_KEY: Optional[str] = None
    TZ_DEFAULT: Optional[str] = None
    LLM_MODEL: Optional[str] = None
    NOTIFY_ENABLED_DEFAULT: Optional[bool] = None
    NOTIFY_HOUR_DEFAULT: Optional[int] = None

    model_config = SettingsConfigDict(
        env_file=".env",  # не мешает Render, но удобен локально
        extra="ignore",
        case_sensitive=True,
    )

    @property
    def EFFECTIVE_BOT_TOKEN(self) -> Optional[str]:
        """Возвращает реальный токен, если он задан любым именем."""
        return self.BOT_TOKEN or self.TG_BOT_TOKEN

    # Удобные предикаты
    @property
    def is_web(self) -> bool:
        return str(self.MODE).lower() == "web"

    @property
    def is_polling(self) -> bool:
        m = str(self.MODE).lower()
        return m in {"polling", "bot"}  # "bot" = синоним для совместимости


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


# Для короткого импорта: from app.config import settings
settings = get_settings()
