# app/main.py
from __future__ import annotations

import asyncio
import hashlib
import importlib
import logging
import os
import sys
import time
from typing import Any

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommand, Message
from fastapi import FastAPI

from app.build import BUILD_MARK
from app.config import settings
from app.storage.repo import ensure_schema

# Роутеры бота
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
    hq,  # HQ-репорт
    # diag — импортируем динамически ниже (нужна особая проверка)
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("main")

START_TIME = time.time()

# Немного ENV для диагностик/веб-статуса
os.environ["UPTIME_SEC"] = "0"   # будет обновляться перед статусом
os.environ.setdefault("MODE", settings.mode)


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


async def _get_status_dict() -> dict[str, Any]:
    uptime = int(time.time() - START_TIME)
    os.environ["UPTIME_SEC"] = str(uptime)  # чтобы diag.api_router тоже видел актуальное значение
    return {
        "build": BUILD_MARK,
        "sha": settings.build_sha or "unknown",
        "uptime_sec": uptime,
        "env": settings.env,
        "mode": settings.mode,
        "bot_id": settings.bot_id or None,
    }


def _make_fallback_ping_router() -> Router:
    """
    Fallback-роутер на случай, если app.routers.ping отсутствует в репозитории.
    Обрабатывает /ping и текст 'ping'.
    """
    r = Router(name="ping_fallback")

    @r.message(F.text.casefold().in_({"/ping", "ping"}))
    async def _ping(msg: Message):
        await msg.answer("pong")

    return r


# ───────────────────────── Polling mode (default) ─────────────────────────
async def run_polling() -> None:
    log.info("=== BUILD %s ===", BUILD_MARK)
    ensure_schema()
    log.info("DB schema ensured")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # На всякий случай чистим webhook
    await _guard(bot.delete_webhook(drop_pending_updates=True), "delete_webhook")

    # ── SMOKE: проверяем экспорты роутеров ────────────────────────────────
    smoke_modules_required = [
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
        "app.routers.diag",  # тут допускаем bot_router или get_router()
    ]
    for modname in smoke_modules_required:
        try:
            mod = importlib.import_module(modname)
            if modname == "app.routers.diag":
                ok = hasattr(mod, "bot_router") or hasattr(mod, "get_router")
                if not ok:
                    raise AssertionError(f"{modname}: expected bot_router or get_router()")
            else:
                if not hasattr(mod, "router"):
                    raise AssertionError(f"{modname}: no `router` export")
        except Exception as e:
            log.error("❌ SMOKE FAIL %s: %r", modname, e)
            sys.exit(1)

    # ping — опциональный: если модуля нет, используем встроенный fallback
    ping_router = None
    try:
        _ping_mod = importlib.import_module("app.routers.ping")
        ping_router = getattr(_ping_mod, "router", None)
        if ping_router is None:
            log.warning("app.routers.ping импортирован, но без `router` — будет использован fallback")
    except ModuleNotFoundError:
        log.info("app.routers.ping не найден — будет использован fallback")

    if ping_router is None:
        ping_router = _make_fallback_ping_router()

    log.info("✅ SMOKE OK: routers exports are valid")

    # ── Подключаем в строгом порядке ──────────────────────────────────────
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
    dp.include_router(ping_router);          log.info("✅ router loaded: ping")

    # diag: поддерживаем bot_router и/или get_router()
    diag_mod = importlib.import_module("app.routers.diag")
    diag_router = getattr(diag_mod, "bot_router", None)
    if diag_router is None:
        factory = getattr(diag_mod, "get_router", None)
        if callable(factory):
            diag_router = factory()
    if diag_router is None:
        raise RuntimeError("app.routers.diag: neither bot_router nor get_router() provided")

    dp.include_router(diag_router);          log.info("✅ router loaded: diag (last)")

    # Команды, инфо, запуск
    await _guard(_set_commands(bot), "set_my_commands")

    token_hash = hashlib.md5(settings.bot_token.encode()).hexdigest()[:8]
    me = await bot.get_me()

    # Сохраним bot_id в ENV, чтобы diag.api_router мог вернуть его
    os.environ["BOT_ID"] = str(me.id)

    log.info("🔑 Token hash: %s", token_hash)
    log.info("🤖 Bot: @%s (ID: %s)", me.username, me.id)
    log.info("🚀 Start polling…")

    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


# ─────────────────────────── Web mode (FastAPI) ───────────────────────────
def run_web() -> FastAPI:
    """
    Factory-функция для uvicorn (factory=True).
    Даёт простой /status_json без лишних зависимостей.
    """
    app = FastAPI(title="Elaya StageCoach", version=BUILD_MARK)

    @app.get("/status_json")
    async def status_json():
        return await _get_status_dict()

    return app


# ───────────────────────────────── entrypoint ─────────────────────────────
if __name__ == "__main__":
    import uvicorn

    if settings.mode.lower() == "web":
        # uvicorn в factory-режиме создаст приложение из run_web()
        uvicorn.run("app.main:run_web", host="0.0.0.0", port=8000, factory=True)
    else:
        try:
            asyncio.run(run_polling())
        except KeyboardInterrupt:
            log.info("⏹ Stopped by user")
