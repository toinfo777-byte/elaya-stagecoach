# app/main.py
from __future__ import annotations

import asyncio
import hashlib
import logging
import importlib
import sys
import time

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommand
from fastapi import FastAPI

from app.config import settings
from app.build import BUILD_MARK
from app.storage.repo import ensure_schema

# aiogram-routers (бот)
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
    hq,
    diag,  # важно: тут теперь есть get_router(mode)
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("main")

START_TIME = time.time()


async def _set_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запуск / меню"),
            BotCommand(command="menu", description="Главное меню"),
            BotCommand(command="levels", description="Тренировка дня"),
            BotCommand(command="progress", description="Мой прогресс"),
            BotCommand(command="help", description="Помощь / FAQ"),
            BotCommand(command="ping", description="Проверка связи"),
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


async def _get_status_dict() -> dict:
    uptime = int(time.time() - START_TIME)
    return {
        "build": BUILD_MARK,
        "sha": settings.build_sha or "unknown",
        "uptime_sec": uptime,
        "env": settings.env,
        "mode": settings.mode,
        "bot_id": settings.bot_id or None,
    }


# ───────────────────────── Polling mode (worker) ─────────────────────────
async def run_polling() -> None:
    log.info("=== BUILD %s ===", BUILD_MARK)
    ensure_schema()
    log.info("DB schema ensured")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Чистим webhook
    await _guard(bot.delete_webhook(drop_pending_updates=True), "delete_webhook")

    # SMOKE: модули должны экспортировать aiogram Router; для diag — get_router/bot_router
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
        "app.routers.hq",
        "app.routers.diag",
    ]
    for modname in smoke_modules:
        try:
            mod = importlib.import_module(modname)
            if modname == "app.routers.diag":
                assert hasattr(mod, "get_router") or hasattr(mod, "bot_router"), \
                    "diag must provide get_router()/bot_router"
            else:
                assert hasattr(mod, "router"), f"{modname}: no `router` export"
        except Exception as e:
            log.error("❌ SMOKE FAIL %s: %r", modname, e)
            sys.exit(1)
    log.info("✅ SMOKE OK: routers exports are valid")

    # Регистрируем aiogram-роутеры в строгом порядке
    dp.include_router(entrypoints.router);   log.info("✅ router loaded: entrypoints")
    dp.include_router(help.router);          log.info("✅ router loaded: help")
    dp.include_router(cmd_aliases.router);   log.info("✅ router loaded: aliases")
    dp.include_router(onboarding.router);    log.info("✅ router loaded: onboarding")
    dp.include_router(system.router);        log.info("✅ router loaded: system")
    dp.include_router(minicasting.router);   log.info("✅ router loaded: minicasting")
    dp.include_router(leader.router);        log.info("✅ router loaded: leader")
    dp.include_router(training.router);      log.info("✅ router loaded: training")
    dp.include_router(progress.router);      log.info("✅ router loaded: progress")
    dp.include_router(privacy.router);       log.info("✅ router loaded: privacy")
    dp.include_router(settings_mod.router);  log.info("✅ router loaded: settings")
    dp.include_router(extended.router);      log.info("✅ router loaded: extended")
    dp.include_router(casting.router);       log.info("✅ router loaded: casting")
    dp.include_router(apply.router);         log.info("✅ router loaded: apply")
    dp.include_router(faq.router);           log.info("✅ router loaded: faq")
    dp.include_router(devops_sync.router);   log.info("✅ router loaded: devops_sync")
    dp.include_router(panic.router);         log.info("✅ router loaded: panic (near last)")
    dp.include_router(hq.router);            log.info("✅ router loaded: hq")
    # ⬇️ главное изменение: берём aiogram-роутер из diag по режиму
    dp.include_router(diag.get_router("worker")); log.info("✅ router loaded: diag (last)")

    await _guard(_set_commands(bot), "set_my_commands")

    token_hash = hashlib.md5(settings.bot_token.encode()).hexdigest()[:8]
    me = await bot.get_me()

    log.info("🔑 Token hash: %s", token_hash)
    log.info("🤖 Bot: @%s (ID: %s)", me.username, me.id)
    log.info("🚀 Start polling…")

    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


# ─────────────────────────── Web mode (FastAPI) ───────────────────────────
def run_web() -> FastAPI:
    """Factory-функция для uvicorn (factory=True)."""
    app = FastAPI(title="Elaya StageCoach", version=BUILD_MARK)

    # Подключаем web-роутер из diag (в нём /status_json)
    app.include_router(diag.get_router("web"))

    # Простой health без лишней инфы
    @app.get("/health")
    async def health():
        return {"ok": True, "mode": "web", **(await _get_status_dict())}

    return app


# ───────────────────────────────── entrypoint ─────────────────────────────
if __name__ == "__main__":
    import uvicorn

    if settings.mode.lower() == "web":
        uvicorn.run("app.main:run_web", host="0.0.0.0", port=8000, factory=True)
    else:
        try:
            asyncio.run(run_polling())
        except KeyboardInterrupt:
            log.info("⏹ Stopped by user")
