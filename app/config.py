from __future__ import annotations

import os
from typing import Literal


def _env(name: str, default: str | None = None) -> str:
    val = os.getenv(name, default)
    if val is None:
        raise RuntimeError(f"ENV {name} is not set")
    return val


class Settings:
    """
    Единая точка конфигурации.
    ВАЖНО:
      - токен читаем из BOT_TOKEN (а не TG_BOT_TOKEN)
      - PARSE_MODE строкой: 'HTML' | 'MarkdownV2' | 'Markdown'
    """
    # Общие
    ENV: str = os.getenv("ENV", "staging")            # staging | prod
    MODE: Literal["web", "worker", "polling"] = os.getenv("MODE", "web")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Сборочные метки (необязательны)
    BUILD_MARK: str = os.getenv("BUILD_MARK", "manual")
    SHORT_SHA: str = os.getenv("SHORT_SHA", "manual_")

    # Telegram
    BOT_TOKEN: str = _env("BOT_TOKEN")                # обязательная во всех режимах
    PARSE_MODE: str = os.getenv("PARSE_MODE", "HTML") # по умолчанию HTML

    # Webhook-база (только для MODE=web)
    # Пример: https://elaya-stagecoach-web.onrender.com
    WEB_BASE_URL: str | None = os.getenv("WEB_BASE_URL")

    @property
    def webhook_url(self) -> str:
        if self.MODE == "web":
            if not self.WEB_BASE_URL:
                raise RuntimeError("ENV WEB_BASE_URL is not set")
            return f"{self.WEB_BASE_URL.rstrip('/')}/tg/{self.BOT_TOKEN}"
        return ""


settings = Settings()
