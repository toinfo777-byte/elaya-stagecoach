# app/main.py
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from app.config import settings
from app.middlewares.error_handler import ErrorsMiddleware
from app.middlewares.source_tags import SourceTagsMiddleware
from app.storage.repo import init_db

# ===== РОУТЕРЫ (явные импорты и порядок важен) =====
from app.routers.smoke import router as smoke_router               # /ping, /health
from app.routers.apply import router as apply_router               # заявка
from app.routers.deeplink import router as deeplink_router         # диплинки /start <payload>
from app.routers.shortcuts import router as shortcuts_router       # /training, /casting, кнопки (в любом состоянии)
from app.routers.reply_shortcuts import router as reply_shortcuts_router
from app.routers.onboarding import router as onboarding_router     # /start
from app.routers.coach import router as coach_router               # наставник
from app.routers.training import router as training_router         # тренировка
from app.routers.casting import router as casting_router           # мини-кастинг
from app.routers.progress import router as progress_router         # прогресс
# ⚠️ старый feedback_router не подключаем
from app.bot.handlers.feedback import router as feedback2_router   # новый универсальный обработчик отзывов
from app.routers.feedback_demo import router as feedback_demo_router  # демо-команда для показа клавиатуры
from app.routers.system import router as system_router             # /help, /privacy, /whoami, /version, /health
from app.routers.settings import router as settings_router         # тех.настройки
from app.routers.admin import router as admin_router               # админка
from app.routers.premium import router as premium_router           # плата/заглушки
from app.routers.metrics import router as metrics_router           # ✅ /metrics (админы)
from app.routers.cancel import router as cancel_router             # глобальная отмена /cancel
from app.routers.debug import router as debug_router               # диагностический — всё в логи
from app.routers.menu import router as menu_router                 # меню (строго последним)

# Обслуживание SQLite
from app.utils.maintenance import backup_sqlite, vacuum_sqlite


# ===== ЛОГИ =====
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("aiogram").setLevel(logging.DEBUG)
logging.getLogger("aiohttp").setLevel(logging.INFO)
logging.getLogger("asyncio").setLevel(logging.INFO)

log = logging.getLogger(__name__)


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
        await _sleep_until_utc(2, 0)  # ежедневно 02:00 UTC
        try:
            path = backup_sqlite()
            log.info("Backup done: %s", path)
        except Exception as e:
            log.exception("Backup failed: %s", e)


async def _vacuum_loop():
    while True:
        await _sleep_until_utc(2, 5, dow=6)  # вс 02:05 UTC
        try:
            vacuum_sqlite()
            log.info("Vacuum done")
        except Exception as e:
            log.exception("Vacuum failed: %s", e)


# ====== меню команд ======
async def setup_commands(bot: Bot) -> None:
    cmds = [
        BotCommand(command="start",     description="Начать"),
        BotCommand(command="apply",     description="Путь лидера (заявка)"),
        BotCommand(command="coach_on",  description="Включить наставника"),
        BotCommand(command="coach_off", description="Выключить наставника"),
        BotCommand(command="ask",       description="Спросить наставника"),
        BotCommand(command="training",  description="Тренировка дня"),
        BotCommand(command="casting",   description="Мини-кастинг"),
        BotCommand(command="progress",  description="Мой прогресс"),
        BotCommand(command="cancel",    description="Сбросить и открыть меню"),
        BotCommand(command="help",      description="Справка"),
        BotCommand(command="privacy",   description="Политика"),
        BotCommand(command="version",   description="Версия"),
        BotCommand(command="feedback_demo", description="Показать клавиатуру отзывов"),
    ]
    await bot.set_my_commands(cmds, scope=BotCommandScopeAllPrivateChats())


# ====== простая прослойка: логируем КАЖДЫЙ апдейт ======
class TraceAllMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        try:
            etype = type(event).__name__
            preview = None
            if hasattr(event, "text") and getattr(event, "text"):
                preview = event.text
            elif hasattr(event, "data") and getattr(event, "data"):
                preview = event.data
            log.info("UPDATE [%s]: %s", etype, preview)
        except Exception:
            log.exception("TraceAllMiddleware logging failed")
        return await handler(event, data)


async def _log_bot_info(bot: Bot) -> None:
    try:
        me = await bot.get_me()
        wh = await bot.get_webhook_info()
        log.info("Bot info: id=%s, username=@%s, name=%s", me.id, me.username, me.first_name)
        log.info(
            "Webhook: url='%s', has_custom_certificate=%s, pending=%s, allowed=%s",
            wh.url or "", getattr(wh, "has_custom_certificate", False),
            getattr(wh, "pending_update_count", 0),
            getattr(wh, "allowed_updates", None),
        )
    except Exception as e:
        log.warning("Failed to read bot/webhook info: %s", e)


# ====== main ======
async def main():
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is empty. Set it in .env")

    init_db()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # middlewares
    dp.update.middleware(TraceAllMiddleware())
    dp.message.middleware(SourceTagsMiddleware())
    dp.callback_query.middleware(SourceTagsMiddleware())
    dp.message.middleware(ErrorsMiddleware())
    dp.callback_query.middleware(ErrorsMiddleware())

    # порядок важен
    for r in (
        smoke_router,
        apply_router,
        deeplink_router,
        shortcuts_router,
        onboarding_router,
        coach_router,
        training_router,
        casting_router,
        progress_router,
        feedback2_router,       # новый обработчик отзывов
        feedback_demo_router,   # команда /feedback_demo
        system_router,
        settings_router,
        admin_router,
        premium_router,
        metrics_router,
        cancel_router,
        debug_router,
        menu_router,
    ):
        dp.include_router(r)
        log.info("Included router: %s", getattr(r, "name", r))

    async with bot:
        try:
            await bot.delete_webhook(drop_pending_updates=False)
        except Exception as e:
            log.warning("delete_webhook failed: %s", e)

        await _log_bot_info(bot)

        try:
            await setup_commands(bot)
        except Exception as e:
            log.warning("setup_commands failed: %s", e)

        asyncio.create_task(_backup_loop())
        asyncio.create_task(_vacuum_loop())

        await dp.start_polling(bot, polling_timeout=30)


if __name__ == "__main__":
    asyncio.run(main())
