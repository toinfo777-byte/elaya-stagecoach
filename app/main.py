# app/main.py
import asyncio
import logging
import importlib
from typing import Optional
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from app.config import settings
from app.middlewares.error_handler import ErrorsMiddleware
from app.storage.repo import init_db

# Базовые роутеры
from app.routers import onboarding, menu
import app.routers.training as training
import app.routers.casting as casting
import app.routers.progress as progress

# Новые фичи
import app.routers.deeplink as deeplink     # <-- НОВОЕ
import app.routers.coach as coach           # <-- НОВОЕ
import app.routers.apply as apply           # заявка «Путь лидера»
import app.routers.feedback as feedback     # сбор отзывов

# Системный роутер
from app.routers import system

# Обслуживание SQLite
from app.utils.maintenance import backup_sqlite, vacuum_sqlite


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


def _include_optional_router(dp: Dispatcher, module_path: str, attr: str = "router") -> Optional[None]:
    try:
        mod = importlib.import_module(module_path)
        r = getattr(mod, attr)
    except Exception as e:
        logging.info("Skip router %s (%s)", module_path, e)
        return None
    dp.include_router(r)
    logging.info("Included router: %s.%s", module_path, attr)
    return None


# ====== фоновые задачи обслуживания БД ======
async def _sleep_until_utc(hour: int, minute: int = 0, dow: int | None = None):
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    target = now.replace(hour=hour, minute=minute)
    if target <= now:
        target += timedelta(days=1)
    if dow is not None:
        while target.weekday() != dow:
            target += timedelta(days=1)
    await asyncio.sleep((target - now).total_seconds())


async def _backup_loop():
    while True:
        await _sleep_until_utc(2, 0)
        try:
            path = backup_sqlite()
            logging.info("Backup done: %s", path)
        except Exception as e:
            logging.exception("Backup failed: %s", e)


async def _vacuum_loop():
    while True:
        await _sleep_until_utc(2, 5, dow=6)
        try:
            vacuum_sqlite()
            logging.info("Vacuum done")
        except Exception as e:
            logging.exception("Vacuum failed: %s", e)
# ==================================================


async def setup_commands(bot: Bot) -> None:
    user_cmds = [
        BotCommand(command="start",     description="Начать"),
        BotCommand(command="menu",      description="Открыть меню"),
        BotCommand(command="training",  description="Тренировка дня"),
        BotCommand(command="progress",  description="Мой прогресс"),
        BotCommand(command="apply",     description="Путь лидера (заявка)"),
        BotCommand(command="privacy",   description="Политика и удаление данных"),
        BotCommand(command="help",      description="Справка"),
    ]
    await bot.set_my_commands(user_cmds, scope=BotCommandScopeAllPrivateChats())


async def main():
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is empty. Set it in .env")

    init_db()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(ErrorsMiddleware())
    dp.callback_query.middleware(ErrorsMiddleware())

    # Служебные (если есть)
    _include_optional_router(dp, "app.routers.settings")
    _include_optional_router(dp, "app.routers.admin")
    _include_optional_router(dp, "app.routers.premium")

    # Порядок: сначала диплинки и коуч, затем основные
    dp.include_router(deeplink.router)   # <-- до онбординга
    dp.include_router(coach.router)      # <-- наставник
    dp.include_router(apply.router)
    dp.include_router(onboarding.router)
    dp.include_router(training.router)
    dp.include_router(casting.router)
    dp.include_router(progress.router)
    dp.include_router(feedback.router)

    # Системный и меню — в конце
    dp.include_router(system.router)
    dp.include_router(menu.router)

    async with bot:
        try:
            await bot.delete_webhook(drop_pending_updates=False)
        except Exception as e:
            logging.warning("delete_webhook failed: %s", e)

        try:
            await setup_commands(bot)
        except Exception as e:
            logging.warning("setup_commands failed: %s", e)

        asyncio.create_task(_backup_loop())
        asyncio.create_task(_vacuum_loop())

        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            polling_timeout=30,
        )


if __name__ == "__main__":
    asyncio.run(main())
