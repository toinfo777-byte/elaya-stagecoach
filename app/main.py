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
from app.routers.feedback import router as feedback2_router        # ✅ новый универсальный фидбек
from app.routers.feedback import kb as feedback_kb_mod             # (экспорт клавы, если нужно из сценариев)
from app.routers.feedback_demo import router as feedback_demo_router  # демо
from app.routers.feedback_old import router as feedback_router     # если у вас есть старый проектный
from app.routers.system import router as system_router             # /help, /privacy, /whoami, /version, /health
from app.routers.settings import router as settings_router         # тех.настройки
from app.routers.admin import router as admin_router               # админка
from app.routers.premium import router as premium_router           # плата/заглушки
from app.routers.metrics import router as metrics_router           # /metrics (админы)
from app.routers.cancel import router as cancel_router             # глобальная отмена /cancel
from app.routers.menu import router as menu_router                 # меню (строго последним)
from app.routers.debug import router as debug_router               # диагностический

# ===== ЛОГИ =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)
logging.getLogger("aiogram").setLevel(logging.INFO)


# ===== служебные фоновые задачи для SQLite (опционально) =====
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
    from app.utils.maintenance import backup_sqlite
    while True:
        await _sleep_until_utc(2, 0)  # ежедневно 02:00 UTC
        try:
            path = backup_sqlite()
            log.info("Backup done: %s", path)
        except Exception:
            log.exception("Backup failed")


async def _vacuum_loop():
    from app.utils.maintenance import vacuum_sqlite
    while True:
        await _sleep_until_utc(2, 5, dow=6)  # вс 02:05 UTC
        try:
            vacuum_sqlite()
            log.info("Vacuum done")
        except Exception:
            log.exception("Vacuum failed")


# ===== команды в меню =====
async def setup_commands(bot: Bot) -> None:
    cmds = [
        BotCommand(command="start",     description="Начать"),
        BotCommand(command="apply",     description="Путь лидера (заявка)"),
        BotCommand(command="training",  description="Тренировка дня"),
        BotCommand(command="casting",   description="Мини-кастинг"),
        BotCommand(command="progress",  description="Мой прогресс"),
        BotCommand(command="cancel",    description="Сбросить и открыть меню"),
        BotCommand(command="help",      description="Справка"),
        BotCommand(command="privacy",   description="Политика"),
        BotCommand(command="version",   description="Версия"),
    ]
    await bot.set_my_commands(cmds, scope=BotCommandScopeAllPrivateChats())


# ===== простая трассировка апдейтов =====
class TraceAllMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        try:
            etype = type(event).__name__
            preview = getattr(event, "text", None) or getattr(event, "data", None)
            log.info("UPDATE [%s]: %s", etype, preview)
        except Exception:
            pass
        return await handler(event, data)


async def _log_bot_info(bot: Bot) -> None:
    try:
        me = await bot.get_me()
        wh = await bot.get_webhook_info()
        log.info("Bot info: id=%s, @%s", me.id, me.username)
        log.info("Webhook: url='%s', pending=%s", wh.url or "", getattr(wh, "pending_update_count", 0))
    except Exception as e:
        log.warning("get_me/webhook failed: %s", e)


# ===== main =====
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

    # ВАЖНО: порядок include_router
    for r in (
        smoke_router,
        apply_router,
        deeplink_router,        # диплинки очень рано
        shortcuts_router,       # /training, /casting и кнопки — в любом состоянии
        reply_shortcuts_router,
        onboarding_router,      # /start анкета
        coach_router,
        training_router,
        casting_router,
        progress_router,

        feedback2_router,       # новый универсальный фидбек (🔥/👌/😐/фраза)
        feedback_demo_router,   # демо-кнопка /feedback_demo
        feedback_router,        # если есть «старый» проектный — ниже

        system_router,
        settings_router,
        admin_router,
        premium_router,
        metrics_router,
        cancel_router,
        debug_router,
        menu_router,            # меню — строго последним
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

        # фоны (по желанию)
        # asyncio.create_task(_backup_loop())
        # asyncio.create_task(_vacuum_loop())

        await dp.start_polling(bot, polling_timeout=30)


if __name__ == "__main__":
    asyncio.run(main())
