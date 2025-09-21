from __future__ import annotations

import asyncio
import importlib
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

# Порядок подключения модулей-роутеров
ROUTER_NAMES = [
    "admin",
    "analytics",
    "reply_shortcuts",
    "cancel",
    "onboarding",
    "menu",
    "training",
    "casting",
    "progress",
    "apply",
    "privacy",
    "help",
    "settings",
    "feedback",
    "shortcuts",
    "deeplink",
]


def _import_router(name: str):
    """
    Пытаемся импортировать модуль и достать из него объект `router`.
    Поддерживаем 2 варианта путей: app.routers.<name> и app.<name>.
    """
    for modname in (f"app.routers.{name}", f"app.{name}"):
        try:
            mod = importlib.import_module(modname)
        except Exception as e:
            log.debug("Import miss %s: %s", modname, e)
            continue
        router = getattr(mod, "router", None)
        if router is not None:
            return router
    return None


async def _set_commands(bot: Bot) -> None:
    cmds = [
        BotCommand(command="start", description="Запуск / онбординг"),
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="training", description="Тренировка дня"),
        BotCommand(command="casting", description="Мини-кастинг"),
        BotCommand(command="progress", description="Мой прогресс"),
        BotCommand(command="apply", description="Путь лидера"),
        BotCommand(command="privacy", description="Политика"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="settings", description="Настройки"),
        BotCommand(command="cancel", description="Сбросить форму"),
    ]
    await bot.set_my_commands(cmds)


async def main() -> None:
    # 1) гарантируем схему БД
    ensure_schema()

    # 2) инициализация бота (aiogram 3.7+)
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # 3) подключаем роутеры без дублей
    seen_router_ids: set[int] = set()
    for name in ROUTER_NAMES:
        r = _import_router(name)
        if r is None:
            log.warning("Router '%s' NOT found — пропускаю", name)
            continue
        if id(r) in seen_router_ids:
            log.info("Router '%s' уже подключён — пропускаю дубликат", name)
            continue
        dp.include_router(r)
        seen_router_ids.add(id(r))
        log.info("✅ Router '%s' подключён", name)

    # 4) команды
    await _set_commands(bot)
    log.info("✅ Команды установлены")

    # 5) старт long polling
    log.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
