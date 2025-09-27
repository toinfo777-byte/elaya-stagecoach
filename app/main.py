# app/main.py
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema

# ── РОУТЕРЫ, где имя экспорта = router ────────────────────────────────────────
from app.routers import (
    start as r_start,            # r_start.router
    common as r_common_guard,    # r_common_guard.router
    privacy as r_privacy,        # r_privacy.router
    progress as r_progress,      # r_progress.router
    settings as r_settings,      # r_settings.router
    extended as r_extended,      # r_extended.router
    training as r_training,      # r_training.router
    casting as r_casting,        # r_casting.router (если нужен)
    # apply as r_apply,          # ⚠️ legacy-анкету временно НЕ подключаем (см. ниже)
)

# ── РОУТЕРЫ с особыми именами экспорта ────────────────────────────────────────
from app.routers.entrypoints import go as entrypoints_router   # единый вход (команды/кнопки)
from app.routers.help import help_router                       # /help + меню/политика/настройки
from app.routers.leader import leader_router                   # 🧭 Путь лидера (новый)
from app.routers.minicasting import mc_router                  # 🎭 Мини-кастинг

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")


async def _set_commands(bot: Bot) -> None:
    cmds = [
        BotCommand(command="start", description="Запуск / онбординг"),
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="training", description="Тренировка дня"),
        BotCommand(command="casting", description="Мини-кастинг"),
        BotCommand(command="apply", description="Путь лидера"),
        BotCommand(command="progress", description="Мой прогресс"),
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

    # 3) анти-конфликт long polling: убираем webhook и срезаем висячие апдейты
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Webhook deleted, pending updates dropped")

    # 4) порядок подключения ВАЖЕН
    #    Сначала единая точка входа (команды/кнопки), затем профильные роутеры.
    dp.include_router(entrypoints_router)   # ← перехватывает /menu, /training, тексты из Reply и go:*
    dp.include_router(r_start.router)       # /start и диплинки

    # FSM-сценарии
    dp.include_router(mc_router)            # 🎭 Мини-кастинг
    dp.include_router(leader_router)        # 🧭 Путь лидера (новый сценарий)

    # глобальные/общие
    dp.include_router(r_common_guard.router)
    dp.include_router(help_router)          # /help, go:menu, go:privacy, go:settings
    dp.include_router(r_privacy.router)
    dp.include_router(r_progress.router)
    dp.include_router(r_settings.router)
    dp.include_router(r_extended.router)

    # прочие сценарии
    dp.include_router(r_training.router)
    dp.include_router(r_casting.router)

    # ⚠️ legacy «apply»-анкета может перехватывать «🧭 Путь лидера» как текст.
    #    Если нужна — верните строку ниже, но измените триггеры внутри роута на уникальные (например, /apply_legacy, callback_data="legacy:*").
    # dp.include_router(r_apply.router)

    # 5) команды
    await _set_commands(bot)
    log.info("✅ Команды установлены")

    # 6) polling
    log.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
