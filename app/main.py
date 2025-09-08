# app/main.py
import asyncio
import logging
import importlib
from typing import Optional
from datetime import datetime, timedelta, timezone  # NEW

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats  # <-- для setup_commands

from app.config import settings
from app.middlewares.error_handler import ErrorsMiddleware
from app.storage.repo import init_db

# Базовые роутеры (точно есть)
from app.routers import onboarding
import app.routers.training as training
import app.routers.casting as casting
import app.routers.progress as progress
from app.routers import menu

# ⬇️ НОВОЕ: заявка «Путь лидера» и сбор отзывов
import app.routers.apply as apply
import app.routers.feedback as feedback

# ⬇️ НОВОЕ: системный роутер (/help, /privacy и техкоманды)
from app.routers import system

# ⬇️ НОВОЕ: утилиты обслуживания SQLite (бэкап и VACUUM)
from app.utils.maintenance import backup_sqlite, vacuum_sqlite


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


def _include_optional_router(dp: Dispatcher, module_path: str, attr: str = "router") -> Optional[None]:
    """
    Пытаемся подключить роутер из module_path.attr.
    Если ничего нет — просто логируем и идём дальше.
    """
    try:
        mod = importlib.import_module(module_path)
        r = getattr(mod, attr)
    except Exception as e:
        logging.info("Skip router %s (%s)", module_path, e)
        return None
    dp.include_router(r)
    logging.info("Included router: %s.%s", module_path, attr)
    return None


# ====== NEW: фоновые задачи обслуживания БД ======

async def _sleep_until_utc(hour: int, minute: int = 0, dow: int | None = None):
    """
    Засыпает до ближайшего времени UTC hour:minute.
    Если указан dow (0=Mon..6=Sun) — до ближайшего такого дня недели.
    """
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    target = now.replace(hour=hour, minute=minute)
    if target <= now:
        target += timedelta(days=1)
    if dow is not None:
        while target.weekday() != dow:
            target += timedelta(days=1)
    await asyncio.sleep((target - now).total_seconds())


async def _backup_loop():
    """Ежедневно в 02:00 UTC делаем копию /data/elaya.db в /data/backups/."""
    while True:
        await _sleep_until_utc(2, 0)  # каждый день 02:00 UTC
        try:
            path = backup_sqlite()
            logging.info("Backup done: %s", path)
        except Exception as e:
            logging.exception("Backup failed: %s", e)


async def _vacuum_loop():
    """Раз в неделю (вс) 02:05 UTC делаем VACUUM для sqlite."""
    while True:
        await _sleep_until_utc(2, 5, dow=6)  # воскресенье 02:05 UTC
        try:
            vacuum_sqlite()
            logging.info("Vacuum done")
        except Exception as e:
            logging.exception("Vacuum failed: %s", e)

# ==================================================


# --- установка /команд в меню ---
async def setup_commands(bot: Bot) -> None:
    user_cmds = [
        BotCommand(command="start",     description="Начать"),
        BotCommand(command="apply",     description="Путь лидера (заявка)"),
        BotCommand(command="coach_on",  description="Включить наставника"),
        BotCommand(command="coach_off", description="Выключить наставника"),
        BotCommand(command="ask",       description="Спросить наставника"),
        BotCommand(command="help",      description="Справка"),
        BotCommand(command="privacy",   description="Политика"),
    ]
    await bot.set_my_commands(user_cmds, scope=BotCommandScopeAllPrivateChats())


async def main():
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is empty. Set it in .env")

    # Инициализируем БД/таблицы и добавочные колонки
    init_db()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # Глобальная обработка ошибок
    dp.message.middleware(ErrorsMiddleware())
    dp.callback_query.middleware(ErrorsMiddleware())

    # 1) Специализированные/служебные роутеры
    _include_optional_router(dp, "app.routers.settings")
    _include_optional_router(dp, "app.routers.admin")
    _include_optional_router(dp, "app.routers.premium")

    # 2) Основные фичи (apply раньше онбординга)
    dp.include_router(apply.router)
    dp.include_router(onboarding.router)
    dp.include_router(training.router)
    dp.include_router(casting.router)
    dp.include_router(progress.router)
    dp.include_router(feedback.router)

    # 3) Системный роутер
    dp.include_router(system.router)

    # 4) Меню — строго последним
    dp.include_router(menu.router)

    # Стартуем polling
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
