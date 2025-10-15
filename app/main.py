# app/main.py
from __future__ import annotations
import asyncio
import hashlib
import logging
import importlib
import sys
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommand

from app.config import settings
from app.build import BUILD_MARK
from app.storage.repo import ensure_schema

# Импортируем только router из всех стабильных модулей
from app.routers import (
    entrypoints,
    help,
    cmd_aliases,
    onboarding,
    system,
    minicasting,
    leader,
    training,
    progress,
    privacy,
    settings as settings_mod,
    extended,
    casting,
    apply,
    faq,
    devops_sync,
    panic,
    diag,
    healthcheck,  # ⬅️ новый роутер
)

# фоновый heartbeat
from app.health import start as health_start

# лог-левел из настроек (если есть), иначе INFO
level_name = getattr(settings, "log_level", "INFO")
logging.basicConfig(
    level=getattr(logging, str(level_name).upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("main")

# Опционально: Sentry (если есть SENTRY_DSN в settings или ENV)
try:
    sentry_dsn = getattr(settings, "sentry_dsn", None) or os.getenv("SENTRY_DSN")
    if sentry_dsn:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[LoggingIntegration(level=logging.WARNING, event_level=logging.ERROR)],
            traces_sample_rate=0.0,
        )
        log.info("Sentry enabled")
except Exception as e:
    log.warning("Sentry init failed: %r", e)


async def _set_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запуск / меню"),
            BotCommand(command="menu", description="Главное меню"),
            BotCommand(command="levels", description="Тренировка дня"),
            BotCommand(command="progress", description="Мой прогресс"),
            BotCommand(command="help", description="Помощь / FAQ"),
            BotCommand(command="ping", description="Проверка связи"),
            BotCommand(command="health", description="Диагностика / аптайм"),
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
    ensure_schema()
    log.info("DB schema ensured")

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Удаляем webhook (если был)
    await _guard(bot.delete_webhook(drop_pending_updates=True), "delete_webhook")

    # ── SMOKE CHECK ────────────────────────────────────────────────
    smoke_modules = [
        "app.routers.entrypoints",
        "app.routers.help",
        "app.routers.cmd_aliases",
        "app.routers.onboarding",
        "app.routers.system",
        "app.routers.minicasting",
        "app.routers.leader",
        "app.routers.training",
        "app.routers.progress",
        "app.routers.privacy",
        "app.routers.settings",
        "app.routers.extended",
        "app.routers.casting",
        "app.routers.apply",
        "app.routers.faq",
        "app.routers.devops_sync",
        "app.routers.panic",
        "app.routers.diag",
        "app.routers.healthcheck",  # ⬅️ добавили в smoke
    ]
    for modname in smoke_modules:
        try:
            mod = importlib.import_module(modname)
            assert hasattr(mod, "router"), f"{modname}: no `router` export"
        except Exception as e:
            log.error("❌ SMOKE FAIL %s: %r", modname, e)
            sys.exit(1)
    log.info("✅ SMOKE OK: routers exports are valid")
    # ───────────────────────────────────────────────────────────────

    # Регистрируем роутеры в строгом порядке
    dp.include_router(entrypoints.router); log.info("✅ router loaded: entrypoints")
    dp.include_router(help.router); log.info("✅ router loaded: help")
    dp.include_router(cmd_aliases.router); log.info("✅ router loaded: aliases")
    dp.include_router(onboarding.router); log.info("✅ router loaded: onboarding")
    dp.include_router(system.router); log.info("✅ router loaded: system")
    dp.include_router(healthcheck.router); log.info("✅ router loaded: healthcheck")  # ⬅️ новый
    dp.include_router(minicasting.router); log.info("✅ router loaded: minicasting")
    dp.include_router(leader.router); log.info("✅ router loaded: leader")
    dp.include_router(training.router); log.info("✅ router loaded: training")
    dp.include_router(progress.router); log.info("✅ router loaded: progress")
    dp.include_router(privacy.router); log.info("✅ router loaded: privacy")
    dp.include_router(settings_mod.router); log.info("✅ router loaded: settings")
    dp.include_router(extended.router); log.info("✅ router loaded: extended")
    dp.include_router(casting.router); log.info("✅ router loaded: casting")
    dp.include_router(apply.router); log.info("✅ router loaded: apply")
    dp.include_router(faq.router); log.info("✅ router loaded: faq")
    dp.include_router(devops_sync.router); log.info("✅ router loaded: devops_sync")
    dp.include_router(panic.router); log.info("✅ router loaded: panic (near last)")
    dp.include_router(diag.router); log.info("✅ router loaded: diag (last)")

    await _guard(_set_commands(bot), "set_my_commands")

    # стартуем фоновый heartbeat (если HEALTHCHECKS_URL задан в ENV)
    loop = asyncio.get_running_loop()
    health_start(loop)

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
