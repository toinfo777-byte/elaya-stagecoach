# app/main.py
from __future__ import annotations
import asyncio
import hashlib
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommand

from app.config import settings
from app.build import BUILD_MARK
from app.storage.repo import ensure_schema  # фиксированный импорт

# Роутеры (безопасный, минимально-достаточный набор)
from app.routers.help import help_router
from app.routers.entrypoints import go_router as entry_router
from app.routers.cmd_aliases import router as aliases_router
from app.routers.onboarding import router as onboarding_router
from app.routers.system import router as system_router
from app.routers.minicasting import router as mc_router
from app.routers.leader import router as leader_router
from app.routers.training import router as training_router
from app.routers.progress import router as progress_router
from app.routers.privacy import router as privacy_router
from app.routers.settings import router as settings_router
from app.routers.extended import router as extended_router
from app.routers.casting import router as casting_router
from app.routers.apply import router as apply_router
from app.routers.faq import router as faq_router
from app.routers.devops_sync import router as devops_sync_router
from app.routers.panic import router as panic_router
from app.routers.diag import router as diag_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("main")


async def _set_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запуск / меню"),
            BotCommand(command="menu", description="Главное меню"),
            BotCommand(command="ping", description="Проверка связи"),
            BotCommand(command="build", description="Текущий билд"),
            BotCommand(command="who", description="Инфо о боте / token-hash"),
            BotCommand(command="webhook", description="Статус вебхука"),
            BotCommand(command="panicmenu", description="Диагностическая клавиатура"),
            BotCommand(command="panicoff", description="Скрыть клавиатуру"),
            BotCommand(command="sync_status", description="Синхронизировать штабные файлы с GitHub"),
        ]
    )


async def _guard(coro, what: str):
    try:
        return await coro
    except TelegramBadRequest as e:
        if "Logged out" in str(e):
            log.warning("%s: Bot API 'Logged out' — игнорируем", what)
            return
        raise


async def main() -> None:
    log.info("=== BUILD %s ===", BUILD_MARK)

    # Чёткий контракт storage
    ensure_schema()
    log.info("DB schema ensured")

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Чистый старт без «висящего» вебхука
    await _guard(bot.delete_webhook(drop_pending_updates=True), "delete_webhook")

    # Порядок: навигация → контент → утилиты → devops → panic → diag
    dp.include_router(entry_router);       log.info("✅ router loaded: entrypoints")
    dp.include_router(help_router);        log.info("✅ router loaded: help")
    dp.include_router(aliases_router);     log.info("✅ router loaded: aliases")
    dp.include_router(onboarding_router);  log.info("✅ router loaded: onboarding")
    dp.include_router(system_router);      log.info("✅ router loaded: system")

    dp.include_router(mc_router);          log.info("✅ router loaded: minicasting")
    dp.include_router(leader_router);      log.info("✅ router loaded: leader")
    dp.include_router(training_router);    log.info("✅ router loaded: training")
    dp.include_router(progress_router);    log.info("✅ router loaded: progress")
    dp.include_router(privacy_router);     log.info("✅ router loaded: privacy")
    dp.include_router(settings_router);    log.info("✅ router loaded: settings")
    dp.include_router(extended_router);    log.info("✅ router loaded: extended")
    dp.include_router(casting_router);     log.info("✅ router loaded: casting")
    dp.include_router(apply_router);       log.info("✅ router loaded: apply")
    dp.include_router(faq_router);         log.info("✅ router loaded: faq")

    dp.include_router(devops_sync_router); log.info("✅ router loaded: devops_sync")
    dp.include_router(panic_router);       log.info("✅ router loaded: panic (near last)")
    dp.include_router(diag_router);        log.info("✅ router loaded: diag (last)")

    await _guard(_set_commands(bot), "set_my_commands")

    # Безопасный хеш токена (в Aiogram 3 нет bot.get_token())
    token_hash = hashlib.md5(settings.bot_token.encode()).hexdigest()[:8]

    me = await bot.get_me()
    log.info("🔑 Token hash: %s", token_hash)
    log.info("🤖 Bot: @%s (ID: %s)", me.username, me.id)
    log.info("🚀 Start polling…")

    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("⏹ Stopped by user")
