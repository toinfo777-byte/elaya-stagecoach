from __future__ import annotations

import asyncio
import importlib
import logging
import os
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from app.config import settings

# === Логирование ===============================================================
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "DEBUG"),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
log = logging.getLogger("main")

# === Настройки ================================================================
BOT_TOKEN = settings.bot_token or os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Не найден BOT_TOKEN. Укажи переменную окружения BOT_TOKEN или settings.bot_token")

DATABASE_URL = settings.db_url or os.getenv("DATABASE_URL", "sqlite:///elaya.db")


# === Вспомогалки ==============================================================
def _import_router(module_base: str, name: str):
    """
    Пытаемся импортировать роутер из:
      1) app.routers.<name>  (переменная router внутри модуля)
      2) app.routers.<name>.router (если роутер лежит подмодулем)
    Возвращает объект Router или None.
    """
    candidates = [
        f"{module_base}.{name}",
        f"{module_base}.{name}.router",
    ]
    for cand in candidates:
        try:
            mod = importlib.import_module(cand)
            # a) сам модуль — если он уже router
            if getattr(mod, "__class__", None).__name__ == "Router":
                return mod
            # b) поле router внутри модуля
            router = getattr(mod, "router", None)
            if router is not None:
                return router
        except Exception as e:
            log.debug("Import miss: %s (%s)", cand, e)
    return None


def _include_router_try_both(dp: Dispatcher, name: str):
    router = _import_router("app.routers", name)
    if router is None:
        log.warning("Router '%s' NOT found — пропускаю", name)
        return False
    dp.include_router(router)
    log.info("✅ Router '%s' подключён: %s", name, router)
    return True


async def _set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить / перезапустить"),
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="training", description="Тренировка"),
        BotCommand(command="progress", description="Мой прогресс"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="cancel", description="Отменить текущее действие"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())
    log.info("✅ /команды установлены для приватных чатов")


# === Bootstrap ================================================================
def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    routers_order = [
        # базовые
        "system",
        "deeplink",
        "cancel",

        # онбординг и маленькое меню
        "onboarding",
        "reply_shortcuts",

        # основное
        "menu",
        "training",
        "casting",
        "progress",
        "apply",
        "premium",
        "privacy",
        "help",

        # отзывы/оценки
        "feedback",

        # шорткаты и настройки
        "shortcuts",
        "settings",

        # отчёты/аналитика
        "analytics",
    ]

    for name in routers_order:
        _include_router_try_both(dp, name)

    return dp


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = build_dispatcher()

    await _set_commands(bot)

    log.info("🚀 Starting long polling…")
    await dp.start_polling(bot, allowed_updates=None)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Bot stopped.")
