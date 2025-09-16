# app/main.py
from __future__ import annotations

import asyncio
import logging
import os
import inspect
from typing import Any, Callable

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

# === Настройки ================================================================
try:
    # ваш pydantic Settings
    from app.config import settings  # type: ignore
except Exception:  # запасной план — работаем только с ENV
    settings = None  # noqa: N816

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("app.main")


def _resolve_token() -> str:
    # 1) settings.BOT_TOKEN (приоритет)
    if settings is not None and getattr(settings, "BOT_TOKEN", None):
        return settings.BOT_TOKEN  # type: ignore[attr-defined]
    # 2) альтернативные имена в Settings (на всякий случай)
    for name in ("API_TOKEN", "TELEGRAM_TOKEN", "ELAYA_BOT_TOKEN"):
        if settings is not None and getattr(settings, name, None):
            return getattr(settings, name)  # type: ignore[no-any-return]
    # 3) переменные окружения
    for env_name in ("BOT_TOKEN", "API_TOKEN", "TELEGRAM_TOKEN", "ELAYA_BOT_TOKEN"):
        val = os.getenv(env_name)
        if val:
            return val
    raise RuntimeError(
        "Bot token not found. "
        "Provide BOT_TOKEN (or API_TOKEN/TELEGRAM_TOKEN/ELAYA_BOT_TOKEN) "
        "via app.config.settings or environment."
    )


async def _maybe_await(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Аккуратно вызвать sync/async функцию."""
    if inspect.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    return fn(*args, **kwargs)


async def _init_db_if_available() -> None:
    """
    Мягкая инициализация БД:
    - если есть app.storage.repo.init_db – вызовем (sync/async);
    - если нет – только предупредим в логах, не падаем.
    """
    try:
        from ap
