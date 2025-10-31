from __future__ import annotations
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Универсальная конфигурация Элайи.
    Совместима с Pydantic v2 и Render Environment.
    """

    # ───────────────────────────────
    # Основное окружение
    # ───────────────────────────────
    ENV: str = os.getenv("ENV", "develop")
    MODE: str = os.getenv("MODE", "worker")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ───────────────────────────────
    # Telegram
    # ───────────────────────────────
    TG_BOT_TOKEN: str | None = os.getenv("TG_BOT_TOKEN")
    BOT_TOKEN: str | None = os.getenv("BOT_TOKEN")
    ADMIN_IDS: str | None = os.getenv("ADMIN_IDS")
    ADMIN_ALERT_CHAT_ID: str | None = os.getenv("ADMIN_ALERT_CHAT_ID")

    # ───────────────────────────────
    # Render API
    # ───────────────────────────────
    RENDER_API_KEY: str | None = os.getenv("RENDER_API_KEY")
    RENDER_SERVICE_ID: str | None = os.getenv("RENDER_SERVICE_ID")
    RENDER_SERVICE_LABELS: str | None = os.getenv("RENDER_SERVICE_LABELS")

    # ───────────────────────────────
    # Build / Deploy
    # ───────────────────────────────
    BUILD_MARK: str = os.getenv("BUILD_MARK", "manual")
    BUILD_SHA: str | None = os.getenv("BUILD_SHA")

    # ───────────────────────────────
    # Прочие опции
    # ───────────────────────────────
    LLM_ENABLED: bool = os.getenv("LLM_ENABLED", "false").lower() == "true"
    LLM_MODEL: str | None = os.getenv("LLM_MODEL")
    IMAGE_TAG: str | None = os.getenv("IMAGE_TAG")

    HQ_REPORT_DIR: str = os.getenv("HQ_REPORT_DIR", "/tmp")
    COACH_RATE_SEC: str | None = os.getenv("COACH_RATE_SEC")
    COACH_TTL_MIN: str | None = os.getenv("COACH_TTL_MIN")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
