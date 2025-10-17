# app/main.py
from __future__ import annotations
import asyncio
import logging
import os
from importlib import import_module
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.observability import setup_observability
from app.observability.health import start_healthcheck

# -----------------------------------------------------------------------------
# Константы окружения
# -----------------------------------------------------------------------------
RELEASE = os.getenv("SHORT_SHA", "local").strip() or "local"
ENV = os.getenv("ENV", "develop").strip() or "develop"
BUILD_AT = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

# -----------------------------------------------------------------------------
# Логирование
# -----------------------------------------------------------------------------
def _setup_logging_from_env() -> None:
    raw = (os.getenv("LOG_LEVEL") or "INFO").strip().upper()
    level = getattr(logging, raw, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logging.info("Logging level set to: %s", raw)

# -----------------------------------------------------------------------------
# Основная логика
# -----------------------------------------------------------------------------
async def main() -> None:
    _setup_logging_from_env()

    token = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Bot token is not set")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # --- /version команда -----------------------------------------------------
    @dp.message(commands=["version"])
    async def cmd_version(message: types.Message):
        text = (
            f"<b>Elaya — Trainer Scene | Dev</b>\n"
            f"🌿 <b>Release:</b> <code>{RELEASE}</code>\n"
            f"🏗 <b>Environment:</b> <code>{ENV}</code>\n"
            f"🕰 <b>Built at:</b> <code>{BUILD_AT}</code>"
        )
        await message.answer(text)

    # --- Подключаем остальные роутеры ----------------------------------------
    routers = [
        "entrypoints", "help", "aliases", "onboarding", "system",
        "minicasting", "leader", "training", "progress", "privacy",
        "settings", "extended", "casting", "apply", "faq",
        "devops_sync", "panic", "diag"
    ]
    for name in routers:
        try:
            module = import_module(f"app.routers.{name}")
            dp.include_router(getattr(module, "router"))
            logging.info("✅ router loaded: %s", name)
        except Exception as e:
            logging.warning("⚠️ router not found: %s (%s)", name, e)

    # --- Запуск heartbeat -----------------------------------------------------
    start_healthcheck()

    logging.info("=== BUILD %s | ENV %s ===", RELEASE, ENV)
    logging.info("🚀 Start polling…")
    await dp.start_polling(bot)

# -----------------------------------------------------------------------------
# Точка входа
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== INIT SENTRY BLOCK EXECUTION ===")
    setup_observability(env=ENV, release=RELEASE, send_test=(ENV != "prod"))
    asyncio.run(main())
