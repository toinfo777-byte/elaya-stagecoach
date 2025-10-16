from __future__ import annotations
import asyncio
import logging
import os
import importlib

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.storage.repo import ensure_schema
from app.build import BUILD_MARK

# ======== OBSERVABILITY / SENTRY =========
from app.observability.sentry import init_sentry, capture_test_message

RELEASE = os.getenv("SHORT_SHA") or "local"
print("=== INIT SENTRY BLOCK EXECUTION ===")
init_sentry(
    dsn=os.getenv("SENTRY_DSN"),
    env=os.getenv("ENV", "prod"),
    release=RELEASE,
)
if os.getenv("ENV", "prod") != "prod":
    capture_test_message()
# ========================================


def include_router_if_exists(dp: Dispatcher, module_name: str, exported_attr: str = "router") -> None:
    """
    Пытается импортировать app.routers.<module_name> и подключить dp.include_router(<module>.router).
    Если модуля или атрибута нет — пишет предупреждение и продолжает.
    """
    full_name = f"app.routers.{module_name}"
    try:
        module = importlib.import_module(full_name)
    except Exception as e:
        logging.warning(f"⚠️ router module not found: {full_name} ({e})")
        return
    router = getattr(module, exported_attr, None)
    if router is None:
        logging.warning(f"⚠️ router attr '{exported_attr}' missing in {full_name}")
        return
    dp.include_router(router)
    logging.info(f"✅ router loaded: {module_name}")


async def main() -> None:
    logging.basicConfig(level=settings.log_level)
    await ensure_schema()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Подключаем все известные роутеры безопасно (порядок важен — оставляем как был)
    for name in [
        "entrypoints",
        "help",
        "aliases",        # если модуля нет — просто будет предупреждение
        "onboarding",
        "system",
        "minicasting",
        "leader",
        "training",
        "progress",
        "privacy",
        "settings",       # экспортит router, в коде модуль может называться settings.py
        "extended",
        "casting",
        "apply",
        "faq",
        "devops_sync",
        "panic",
        "diag",
    ]:
        include_router_if_exists(dp, name)

    logging.info(f"=== BUILD {BUILD_MARK} ===")
    logging.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
