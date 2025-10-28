from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List


def _env(name: str, default: str | None = None) -> str:
    v = os.getenv(name, default)
    if v is None:
        raise RuntimeError(f"ENV {name} is not set")
    return v


@dataclass(frozen=True)
class Settings:
    # Режим: "web" (Render/FastAPI+webhook) или "polling" (локально/воркер)
    MODE: str = os.getenv("MODE", "web").lower()

    # Telegram
    BOT_TOKEN: str = _env("TG_BOT_TOKEN")
    PARSE_MODE: str = os.getenv("TG_PARSE_MODE", "HTML")

    # Веб-часть
    WEB_BASE_URL: str = _env("WEB_BASE_URL")  # например: https://elaya-stagecoach-web.onrender.com
    WEBHOOK_SECRET: str = _env("WEBHOOK_SECRET", "secret-path")  # просто строка
    WEBHOOK_ALLOWED_UPDATES: List[str] = tuple(
        (os.getenv("WEBHOOK_ALLOWED_UPDATES") or "message,callback_query").split(",")
    )

    # Служебное (красивые подписи версий)
    BUILD_MARK: str = os.getenv("BUILD_MARK", "manual_")
    SHORT_SHA: str = os.getenv("SHORT_SHA", "unknown")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Админы (для /control заглушки)
    ADMIN_IDS: List[int] = [
        int(x) for x in (os.getenv("ADMIN_IDS") or "").strip().split(",") if x.strip().isdigit()
    ]


settings = Settings()
