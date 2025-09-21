from __future__ import annotations

import asyncio
import importlib
import logging
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema

log = logging.getLogger("main")


async def _set_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запуск / онбординг"),
            BotCommand(command="menu", description="Открыть меню"),
            BotCommand(command="training", description="Тренировка дня"),
            BotCommand(command="casting", description="Мини-кастинг"),
            BotCommand(command="progress", description="Мой прогресс"),
            BotCommand(command="settings", description="Настройки"),
            BotCommand(command="help", description="Помощь"),
            BotCommand(command="cancel", description="Отмена"),
        ]
    )
    log.info("✅ Команды установлены")


def _try_include(dp: Dispatcher, module_path: str, attr: str = "router") -> None:
    """
    Мягкое подключение роутера: если модуля нет или в нём нет router — просто предупреждение.
    """
    try:
        module = importlib.import_module(module_path)
        router = getattr(module, attr, None)
        if router is None:
            raise AttributeError(f"'{module_path}' has no '{attr}'")
        dp.include_router(router)
        log.info("✅ Router '%s' подключён", module_path.rsplit(".", 1)[-1])
    except Exception as e:
        log.warning("Router '%s' NOT found — пропускаю (%s)", module_path, e)


def setup_routers(dp: Dispatcher) -> None:
    # важен порядок: сначала универсальные шорткаты и cancel, потом онбординг, остальное — ниже
    for mod in [
        "app.routers.reply_shortcuts",
        "app.routers.cancel",
        "app.routers.onboarding",
        "app.routers.menu",
        "app.routers.training",
        "app.routers.casting",
        "app.routers.apply",
        "app.routers.progress",
        "app.routers.settings",
        "app.routers.analytics",
        # опциональные:
        "app.routers.help",
        "app.routers.system",
        "app.routers.shortcuts",
        "app.routers.feedback",
        "app.routers.premium",
        "app.routers.privacy",
    ]:
        _try_include(dp, mod)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    # 1) гарантируем схему БД (создастся, если таблиц нет)
    ensure_schema()

    # 2) aiogram
    bot = Bot(token=settings.bot_token, parse_mode="HTML")
    dp = Dispatcher()

    setup_routers(dp)
    await _set_commands(bot)

    # 3) работаем на long-polling — отключаем вебхук, но апдейты не дропаем
    await bot.delete_webhook(drop_pending_updates=False)

    log.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
