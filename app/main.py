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

BUILD_MARK = "faq-hard-priority-2025-09-28-1827"
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

# ⛔ Больше НЕ включаем help_router и r_common_guard — чтобы они не перехватывали события.
# Их функции мы используем через entrypoints (show_main_menu/…).

# новый FAQ (самостоятельный ровный роутер)
from app.routers.faq import router as faq_router

# остальные разделы
try:
    from app.routers.minicasting import mc_router
except Exception:
    from app.routers.minicasting import router as mc_router

from app.routers.training import router as tr_router
from app.routers.leader import router as leader_router

from app.routers import (
    privacy as r_privacy,
    progress as r_progress,
    settings as r_settings,
    extended as r_extended,
    casting as r_casting,
    apply as r_apply,
    # common as r_common_guard,  # ← БОЛЬШЕ НЕ ПОДКЛЮЧАЕМ
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
        BotCommand(command="help", description="FAQ / помощь"),
        BotCommand(command="settings", description="Настройки"),
        BotCommand(command="cancel", description="Сбросить форму"),
    ]
    await bot.set_my_commands(cmds)

async def main() -> None:
    log.info("=== BUILD %s ===", BUILD_MARK)

    # 1) схема БД
    await ensure_schema()

    # 2) bot/DP
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # 3) срезаем webhook и висячие апдейты
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Webhook deleted, pending updates dropped")

    # 4) входной роутер entrypoints — надёжно через importlib
    ep = importlib.import_module("app.routers.entrypoints")
    go_router = getattr(ep, "go_router", getattr(ep, "router"))
    log.info("entrypoints loaded: using %s", "go_router" if hasattr(ep, "go_router") else "router")

    # 5) Подключение роутеров — без help_router и без common_guard
    dp.include_routers(
        go_router,         # входные точки
        mc_router,         # 🎭 Мини-кастинг
        leader_router,     # 🧭 Путь лидера
        tr_router,         # 🏋️ Тренировка дня
        r_progress.router,
        r_privacy.router,
        r_settings.router,
        r_extended.router,
        r_casting.router,
        r_apply.router,
        faq_router,        # ❓ FAQ / помощь (идёт последним)
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
