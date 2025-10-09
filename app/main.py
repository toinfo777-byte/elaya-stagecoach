from __future__ import annotations
import asyncio
import logging
import hashlib
from inspect import iscoroutinefunction

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema
from app.build import BUILD_MARK
from app.routers.diag import router as diag_router
from app.routers.panic import router as panic_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger("main")


async def _set_commands(bot: Bot) -> None:
    await bot.set_my_commands([
        BotCommand(command="start",     description="Запуск / меню"),
        BotCommand(command="menu",      description="Главное меню"),
        BotCommand(command="ping",      description="Проверка связи"),
        BotCommand(command="build",     description="Текущий билд"),
        BotCommand(command="who",       description="Инфо о боте / token-hash"),
        BotCommand(command="webhook",   description="Статус вебхука"),
        BotCommand(command="panicmenu", description="Диагностическая клавиатура"),
        BotCommand(command="panicoff",  description="Скрыть клавиатуру"),
    ])


async def main() -> None:
    log.info("=== BUILD %s ===", BUILD_MARK)

    # ── Инициализация БД (поддержка sync/async ensure_schema) ──────────────
    try:
        if iscoroutinefunction(ensure_schema):
            await ensure_schema()
        else:
            ensure_schema()
        log.info("DB schema ensured")
    except Exception:
        log.exception("ensure_schema failed")

    # ── Bot/Dispatcher ──────────────────────────────────────────────────────
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Снимаем вебхук и чистим очередь
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Webhook deleted, pending updates dropped")

    dp = Dispatcher()
    dp.include_router(diag_router);  log.info("✅ router loaded: diag")
    dp.include_router(panic_router); log.info("✅ router loaded: panic")

    await _set_commands(bot)

    me = await bot.get_me()
    log.info("🔑 Token hash: %s", hashlib.md5(settings.bot_token.encode()).hexdigest()[:8])
    log.info("🤖 Bot: @%s (ID: %s)", me.username, me.id)
    log.info("🚀 Start polling…")

    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("⏹ Stopped by user")
