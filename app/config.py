from __future__ import annotations

import os
from dataclasses import dataclass


def _get(name: str, *, fallback: str | None = None, required: bool = True) -> str:
    """
    Читает переменную окружения с поддержкой имени-фоллбэка.
    required=False — вернёт пустую строку, если нет ни основного, ни фоллбэка.
    """
    if val := os.getenv(name):
        return val
    if fallback:
        fb = os.getenv(fallback)
        if fb:
            return fb
    if required:
        raise RuntimeError(f"ENV {name} is not set")
    return ""


@dataclass(slots=True)
class Settings:
    # Билд-метки (необязательно)
    BUILD_MARK: str = os.getenv("BUILD_MARK", "manual_")
    SHORT_SHA: str = os.getenv("SHORT_SHA", "manual_")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Среда и режим
    ENV: str = os.getenv("ENV", "staging")               # staging|prod|dev
    MODE: str = os.getenv("MODE", "webhook")             # webhook|polling|web

    # Бот
    # TG_BOT_TOKEN (основной) ← fallback на BOT_TOKEN (как у тебя в Render)
    BOT_TOKEN: str = _get("TG_BOT_TOKEN", fallback="BOT_TOKEN", required=True)

    # База URL для webhook-ов веб-сервиса:
    # WEB_BASE_URL (основной) ← fallback на RENDER_EXTERNAL_URL (Render выставляет автоматом)
    WEB_BASE_URL: str = _get("WEB_BASE_URL", fallback="RENDER_EXTERNAL_URL", required=False)

    # Идентификаторы для /hq (необязательно, просто чтобы красиво печатать)
    STATUS_CHAT_ID: str = os.getenv("TG_STATUS_CHAT_ID", "")

    # Безопасные таймауты/порты
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))


settings = Settings()
