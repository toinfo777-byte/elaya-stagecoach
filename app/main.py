# app/main.py
from __future__ import annotations

import asyncio
import logging
import os
from importlib import import_module

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.observability import setup_observability
from app.observability.health import start_healthcheck

RELEASE = os.getenv("SHORT_SHA", "local").strip() or "local"
ENV = os.getenv("ENV", "develop").strip() or "develop"

try:
    from app.storage import ensure_schema as _ensure_schema  # type: ignore
except Exception:
    _ensure_schema = None  # type: ignore


def ensure_schema() -> None:
    if _ensure_schema is None:
        logging.info("ℹ️  ensure_schema: no-op (module not found)")
        return
    _ensure_schema()
    logging.info("✅ Schema ensured")


def _setup_logging_from_env() -> None:
    raw = (os.getenv("LOG_LEVEL") or "INFO").strip().upper()
    level = {"INFO": "INFO", "DEBUG": "DEBUG", "WARNING": "WARNING", "ERROR": "ERROR"}.get(raw, "INFO")
    logging.basicConfig(level=getattr(logging, level),
                        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    logging.info("Logging level set to: %s", level)


async def main() -> None:
    _setup_logging_from_env()
    ensure_schema()

    token = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Bot token is not set (env var TELEGRAM_TOKEN or BOT_TOKEN)")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    def safe_include(module_name: str, name: str) -> None:
        try:
            module = import_module(module_name)
            dp.include_router(getattr(module, "router"))
            logging.info("✅ router loaded: %s", name)
        except Exception as e:
            logging.warning("⚠️ router module not found: %s (%s)", module_name, e)

    for name in [
        "entrypoints", "help", "aliases", "onboarding", "system", "minicasting", "leader",
        "training", "progress", "privacy", "settings", "extended", "casting", "apply",
        "faq", "devops_sync", "panic", "diag",
    ]:
        safe_include(f"app.routers.{name}", name)

    # Запускаем heartbeat уже в работающем event-loop
    task = start_healthcheck()
    if task:
        logging.info("Observability: heartbeat task started (%s)", task.get_name())

    logging.info("=== BUILD %s ===", RELEASE or "local")
    logging.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("=== INIT SENTRY BLOCK EXECUTION ===")
    setup_observability(env=ENV, release=RELEASE, send_test=(ENV != "prod"))
    asyncio.run(main())
