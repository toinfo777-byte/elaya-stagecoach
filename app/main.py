from __future__ import annotations

import asyncio
import hashlib
import importlib
import logging
import os
import sys
import time
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommand
from fastapi import FastAPI

from app.build import BUILD_MARK
from app.config import settings
from app.storage.repo import ensure_schema

# Роутеры бота
from app.routers import (
    basic,            # ⬅️ НОВОЕ: минимальные /start,/ping
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
    hq,               # HQ-сводка
    # diag — динамически ниже
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("main")

START_TIME = time.time()
os.environ["UPTIME_SEC"] = "0"
os.environ.setdefault("MODE", settings.mode)


async def _set_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запуск / меню"),
            BotCommand(command="ping", description="Проверка связи"),
            BotCommand(command="hq", description="HQ-сводка"),
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

async def _get_status_dict() -> dict[str, Any]:
    uptime = int(time.time() - START_TIME)
    os.environ["UPTIME_SEC"] = str(uptime)
    return {
        "build": BUILD_MARK,
        "sha": settings.build_sha or "unknown",
        "uptime_sec": uptime,
        "env": settings.env,
        "mode": settings.mode,
        "bot_id": settings.bot_id or None,
    }

# ───────────────────────── Polling mode ─────────────────────────
async def run_polling() -> None:
    log.info("=== BUILD %s ===", BUILD_MARK)
    ensure_schema()
    log.info("DB schema ensured")

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    await _guard(bot.delete_webhook(drop_pending_updates=True), "delete_webhook")

    # Подключаем РОУТЕРЫ. Важен порядок!
    dp.include_router(basic.router);         log.info("✅ router loaded: basic")       # Самый первый — всегда отвечает /start,/ping
    dp.include_router(entrypoints.router);   log.info("✅ router loaded: entrypoints")
    dp.include_router(help.router);          log.info("✅ router loaded: help")
    dp.include_router(hq.router);            log.info("✅ router loaded: hq")          # HQ раньше алиасов
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

    # diag — в самом конце; поддерживаем bot_router/get_router
    diag_mod = importlib.import_module("app.routers.diag")
    diag_router = getattr(diag_mod, "bot_router", None)
    if diag_router is None:
        factory = getattr(diag_mod, "get_router", None)
        if callable(factory):
            diag_router = factory()
    if diag_router is None:
        raise RuntimeError("app.routers.diag: neither bot_router nor get_router() provided")
    dp.include_router(diag_router);          log.info("✅ router loaded: diag (last)")

    await _guard(_set_commands(bot), "set_my_commands")

    token_hash = hashlib.md5(settings.bot_token.encode()).hexdigest()[:8]
    me = await bot.get_me()
    os.environ["BOT_ID"] = str(me.id)

    log.info("🔑 Token hash: %s", token_hash)
    log.info("🤖 Bot: @%s (ID: %s)", me.username, me.id)
    log.info("🚀 Start polling…")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])

# ─────────────────────────── Web mode ───────────────────────────
from fastapi import FastAPI
def run_web() -> FastAPI:
    app = FastAPI(title="Elaya StageCoach", version=BUILD_MARK)

    @app.get("/status_json")
    async def status_json():
        return await _get_status_dict()

    return app

if __name__ == "__main__":
    import uvicorn
    if settings.mode.lower() == "web":
        uvicorn.run("app.main:run_web", host="0.0.0.0", port=8000, factory=True)
    else:
        try:
            asyncio.run(run_polling())
        except KeyboardInterrupt:
            log.info("⏹ Stopped by user")
