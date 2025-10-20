from __future__ import annotations

import asyncio
import logging
import os
from importlib import import_module

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from dotenv import load_dotenv
# === Загрузка встроенного .env из образа (впечатанного при сборке) ===
load_dotenv(dotenv_path="/app/.env", override=True)

from app.observability import setup_observability
from app.observability.health import start_heartbeat_if_configured

RELEASE = os.getenv("SHORT_SHA", "local").strip() or "local"
ENV = os.getenv("ENV", "develop").strip() or "develop"

def _setup_logging_from_env() -> None:
    raw = (os.getenv("LOG_LEVEL") or "INFO").strip().upper()
    level = {"INFO": "INFO", "DEBUG": "DEBUG", "WARNING": "WARNING", "ERROR": "ERROR"}.get(raw, "INFO")
    logging.basicConfig(level=getattr(logging, level),
                        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    logging.info(f"Logging level set to: {level}")

async def main() -> None:
    _setup_logging_from_env()

    token = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Bot token is not set (TELEGRAM_TOKEN or BOT_TOKEN)")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Роутеры
    try:
        mod = import_module("app.routers.control")
        dp.include_router(getattr(mod, "router"))
        logging.info("✅ router loaded: control")
    except Exception as e:
        logging.exception("❌ failed to load router control: %s", e)
        raise

    logging.info(f"=== BUILD {RELEASE or 'local'} ===")

    # Heartbeat (Cronitor/HC)
    loop = asyncio.get_running_loop()
    start_heartbeat_if_configured(loop)

    logging.info("🚀 Start polling…")
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("=== INIT SENTRY BLOCK EXECUTION ===")
    setup_observability(env=ENV, release=RELEASE, send_test=(ENV != "prod"))
    asyncio.run(main())
