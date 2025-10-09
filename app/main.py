from __future__ import annotations

import asyncio
import logging
import hashlib
from inspect import iscoroutinefunction

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.exceptions import TelegramBadRequest

from app.config import settings
from app.storage.repo import ensure_schema
from app.build import BUILD_MARK
from app.routers.diag import router as diag_router
from app.routers.panic import router as panic_router


# ────────────────────────── Логирование ──────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("main")


# ─────────────────── Команды бота (может падать) ─────────────────
async def _set_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start",     description="Запуск / меню"),
            BotCommand(command="menu",      description="Главное меню"),
            BotCommand(command="ping",      description="Проверка связи"),
            BotCommand(command="build",     description="Текущий билд"),
            BotCommand(command="who",       description="Инфо о боте / token-hash"),
            BotCommand(command="webhook",   description="Статус вебхука"),
            BotCommand(command="panicmenu", description="Диагностическая клавиатура"),
            BotCommand(command="panicoff",  description="Скрыть клавиатуру"),
        ]
    )


# ───────────── Универсальный «гвард» для Logged out ──────────────
async def _guard_logged_out(coro, *, what: str):
    """
    Оборачивает вызовы методов Bot API, которые могут падать TelegramBadRequest: Logged out.
    В таком случае просто логируем и продолжаем запуск.
    """
    try:
        return await coro
    except TelegramBadRequest as e:
        if "Logged out" in str(e):
            log.warning("%s: Bot API reports 'Logged out' — игнорируем и продолжаем polling", what)
            return None
        raise


# ─────────────────────────── main() ──────────────────────────────
async def main() -> None:
    log.info("=== BUILD %s ===", BUILD_MARK)

    # Инициализация/миграции БД: поддержка sync/async ensure_schema
    try:
        if iscoroutinefunction(ensure_schema):
            await ensure_schema()
        else:
            ensure_schema()
        log.info("DB schema ensured")
    except Exception:
        log.exception("ensure_schema failed")

    # Создаём Bot/Dispatcher
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Снимаем вебхук (если стоял). На некоторых токенах даёт "Logged out" — игнорируем.
    await _guard_logged_out(
        bot.delete_webhook(drop_pending_updates=True),
        what="delete_webhook",
    )

    # Роутеры диагностики
    dp.include_router(diag_router);  log.info("✅ router loaded: diag")
    dp.include_router(panic_router); log.info("✅ router loaded: panic")

    # Попытка выставить команды — может словить "Logged out"
    await _guard_logged_out(_set_commands(bot), what="set_my_commands")

    # Кто мы
    me = await bot.get_me()
    log.info("🔑 Token hash: %s", hashlib.md5(settings.bot_token.encode()).hexdigest()[:8])
    log.info("🤖 Bot: @%s (ID: %s)", me.username, me.id)
    log.info("🚀 Start polling…")

    # Запуск long polling
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("⏹ Stopped by user")
