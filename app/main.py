# app/main.py
from __future__ import annotations
import asyncio, logging, hashlib
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema

# диагностика/паник-слой
from app.build import BUILD_MARK                     # метка билда для логов и /build
from app.routers.diag import router as diag_router   # /build /who /webhook /panicmenu /panicoff /ping
from app.routers.panic import router as panic_router # ответ на любые апдейты + простые кнопки

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("main")

async def _set_commands(bot: Bot) -> None:
    await bot.set_my_commands([
        BotCommand(command="start",     description="Запуск / меню"),
        BotCommand(command="menu",      description="Главное меню"),
        BotCommand(command="ping",      description="Проверка связи"),
        # диагностические:
        BotCommand(command="build",     description="Текущий билд"),
        BotCommand(command="who",       description="Инфо о боте / token-hash"),
        BotCommand(command="webhook",   description="Статус вебхука"),
        BotCommand(command="panicmenu", description="Диагностическая клавиатура"),
        BotCommand(command="panicoff",  description="Скрыть клавиатуру"),
    ])

async def main() -> None:
    log.info("=== BUILD %s ===", BUILD_MARK)
    await ensure_schema()

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Снимаем вебхук и чистим очередь
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Webhook deleted, pending updates dropped")

    # На всякий: выходим из старых long-polling сессий (если где-то второй процесс)
    try:
        await bot.log_out()
        log.info("Logged out previous sessions")
    except Exception:
        log.exception("log_out failed (can ignore)")

    # Создаём новый клиент после log_out
    await bot.session.close()
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()

    # Подключаем сперва диагностический слой, потом «паник»-роутер
    dp.include_router(diag_router)
    log.info("✅ router loaded: diag")
    dp.include_router(panic_router)
    log.info("✅ router loaded: panic")

    await _set_commands(bot)

    me = await bot.get_me()
    log.info("🔑 Token hash: %s", hashlib.md5(settings.bot_token.encode()).hexdigest()[:8])
    log.info("🤖 Bot: @%s (ID: %s)", me.username, me.id)
    log.info("🚀 Start polling…")

    # Явно разрешаем и message, и callback_query
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("⏹ Stopped by user")
