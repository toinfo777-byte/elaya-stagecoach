# app/main.py
from __future__ import annotations

import asyncio
import logging
import os
from importlib import import_module

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.sentry import init_sentry, capture_test_message

# ---------------------------------------------------------------------------
# Константы окружения
# ---------------------------------------------------------------------------

RELEASE = os.getenv("SHORT_SHA", "local").strip() or "local"
ENV = os.getenv("ENV", "develop").strip() or "develop"

# ---------------------------------------------------------------------------
# Обёртка ensure_schema: не падаем, если модуля нет
# ---------------------------------------------------------------------------

try:
    # Если у тебя функция живёт в другом месте — поправь импорт здесь
    from app.storage import ensure_schema as _ensure_schema  # type: ignore
except Exception:
    _ensure_schema = None  # type: ignore


def ensure_schema() -> None:
    """
    Гарантирует наличие схемы/миграций. Не асинхронная.
    Отсутствие функции не считается ошибкой.
    """
    if _ensure_schema is None:
        logging.info("ℹ️  ensure_schema: no-op (module not found)")
        return
    _ensure_schema()
    logging.info("✅ Schema ensured")


# ---------------------------------------------------------------------------
# Настройка логирования
# ---------------------------------------------------------------------------

def _setup_logging_from_env() -> None:
    raw = (os.getenv("LOG_LEVEL") or "INFO").strip().upper()
    level = {
        "INFO": "INFO",
        "DEBUG": "DEBUG",
        "WARNING": "WARNING",
        "ERROR": "ERROR",
    }.get(raw, "INFO")

    logging.basicConfig(level=getattr(logging, level))
    logging.info(f"Logging level set to: {level}")


# ---------------------------------------------------------------------------
# Точка входа
# ---------------------------------------------------------------------------

async def main() -> None:
    _setup_logging_from_env()

    # 1) Схема/миграции (синхронно)
    ensure_schema()

    # 2) Бот и диспетчер
    #    Ожидается, что токен лежит в переменной окружения TELEGRAM_TOKEN или BOT_TOKEN.
    token = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Bot token is not set (env var TELEGRAM_TOKEN or BOT_TOKEN)")

    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # 3) Подключаем роутеры мягко: если модуля нет — просто предупреждаем
    def safe_include(module_name: str, name: str) -> None:
        try:
            module = import_module(module_name)
            dp.include_router(getattr(module, "router"))
            logging.info(f"✅ router loaded: {name}")
        except Exception as e:
            logging.warning(f"⚠️ router module not found: {module_name} ({e})")

    routers = [
        "entrypoints",
        "help",
        "aliases",       # может отсутствовать — это окей
        "onboarding",
        "system",
        "minicasting",
        "leader",
        "training",
        "progress",
        "privacy",
        "settings",
        "extended",
        "casting",
        "apply",
        "faq",
        "devops_sync",
        "panic",
        "diag",
    ]

    for name in routers:
        safe_include(f"app.routers.{name}", name)

    logging.info(f"=== BUILD {RELEASE or 'local'} ===")
    logging.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("=== INIT SENTRY BLOCK EXECUTION ===")
    sentry_ready = init_sentry(env=ENV, release=RELEASE)

    # Шлём тест только вне prod и только если настроен DSN
    if sentry_ready and ENV != "prod":
        capture_test_message()

    asyncio.run(main())
