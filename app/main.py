from __future__ import annotations

import asyncio
import logging
import importlib

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

# --- «мягкие» импорты роутеров, чтобы не падать из-за имён ---
# help: либо help_router, либо router
try:
    from app.routers.help import help_router
except Exception:
    from app.routers.help import router as help_router

# minicasting: либо mc_router, либо router
try:
    from app.routers.minicasting import mc_router
except Exception:
    from app.routers.minicasting import router as mc_router

# training / leader — забираем router под явным именем
from app.routers.training import router as tr_router
from app.routers.leader import router as leader_router

# остальные разделы — через модуль и .router
from app.routers import (
    privacy as r_privacy,
    progress as r_progress,
    settings as r_settings,
    extended as r_extended,
    casting as r_casting,
    apply as r_apply,
    common as r_common_guard,  # глобальный guard в самом конце
)


async def _set_commands(bot: Bot) -> None:
    cmds = [
        BotCommand(command="start", description="Запуск / онбординг"),
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="training", description="Тренировка дня"),
        BotCommand(command="casting", description="Мини-кастинг"),
        BotCommand(command="progress", description="Мой прогресс"),
        BotCommand(command="apply", description="Путь лидера"),
        BotCommand(command="privacy", description="Политика"),
        BotCommand(command="extended", description="Расширенная версия"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="settings", description="Настройки"),
        BotCommand(command="cancel", description="Сбросить форму"),
    ]
    await bot.set_my_commands(cmds)


async def main() -> None:
    # 1) схема БД
    await ensure_schema()

    # 2) бот/DP
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # 3) обнуляем webhook и висячие апдейты
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Webhook deleted, pending updates dropped")

    # 4) входной роутер — БЕЗ топ-импорта: динамически через importlib
    ep = importlib.import_module("app.routers.entrypoints")
    go_router = getattr(ep, "go_router", getattr(ep, "router"))
    log.info("entrypoints loaded: using %s", "go_router" if hasattr(ep, "go_router") else "router")

    # 5) подключение роутеров (порядок важен)
    dp.include_routers(
        # входной роутер — первым
        go_router,

        # FSM-сценарии — до «common guard»
        mc_router,        # 🎭 Мини-кастинг
        leader_router,    # 🧭 Путь лидера
        tr_router,        # 🏋️ Тренировка дня

        # разделы
        r_progress.router,
        r_privacy.router,
        r_settings.router,
        r_extended.router,
        r_casting.router,
        r_apply.router,

        # /help и экран меню/политика/настройки
        help_router,

        # глобальный «гвард» — САМЫЙ ПОСЛЕДНИЙ
        r_common_guard.router,
    )

    # 6) команды
    await _set_commands(bot)
    log.info("✅ Команды установлены")

    # 7) polling
    log.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("⏹ Stopped by user")
