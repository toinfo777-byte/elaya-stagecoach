from __future__ import annotations

import os
from typing import Literal, Optional


def _env(name: str, default: Optional[str] = None, required: bool = False) -> str:
    val = os.getenv(name, default)
    if required and (val is None or val == ""):
        raise RuntimeError(f"ENV {name} is not set")
    return val


class Settings:
    # Режим запуска (влияет на entrypoint через ENV, но дублируем для логов/поведения)
    MODE: Literal["worker", "web"] = _env("MODE", "web")

    # Токен бота: ИСПОЛЬЗУЕМ ИМЕННО BOT_TOKEN (по скринам у тебя так)
    BOT_TOKEN: str = _env("BOT_TOKEN", required=True)

    # Парс-мод по умолчанию — нужен для aiogram.DefaultBotProperties
    PARSE_MODE: str = _env("PARSE_MODE", "HTML")  # HTML | MarkdownV2

    # Базовый URL веб-сервиса (для линков в HQ-отчёте и т.п.)
    WEB_BASE_URL: str = _env("WEB_BASE_URL", "http://localhost:8000")

    # Метки билда/деплоя (если Render их прокидывает — используем, иначе safe default)
    RENDER_GIT_COMMIT: str = os.getenv("RENDER_GIT_COMMIT", "manual")
    RENDER_SERVICE_NAME: str = os.getenv("RENDER_SERVICE_NAME", "local")

    # Прочие ID чатов/метрики и т.п. — оставь как у тебя заведено:
    TG_STATUS_CHAT_ID: Optional[str] = os.getenv("TG_STATUS_CHAT_ID")  # не required


settings = Settings()
