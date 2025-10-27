from __future__ import annotations

import asyncio
import hashlib
import importlib
import logging
import os
import sys
import time
from typing import Any, Optional

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramConflictError
from aiogram.types import BotCommand, Message
from fastapi import FastAPI

from app.build import BUILD_MARK
from app.config import settings
from app.storage.repo import ensure_schema

# Роутеры бота
from app.routers import (
    entrypoints,
    help as help_router,
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
            BotCommand(command="whoami", description="Текущий бот / среда"),
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


def _make_fallback_ping_router() -> Router:
    r = Router(name="ping_fallback")

    @r.message(F.text.casefold().in_({"/ping", "ping"}))
    async def _ping(msg: Message):
        await msg.answer("pong")

    @r.message(F.text.casefold() == "/whoami")
    async def _whoami(msg: Message, bot: Bot):
        me = await bot.get_me()
        await msg.answer(
            f"🤖 <b>whoami</b>\n"
            f"• username: <code>@{me.username}</code>\n"
            f"• bot_id: <code>{me.id}</code>\n"
            f"• ENV: <code>{settings.env}</code>\n"
            f"• MODE: <code>{settings.mode}</code>\n"
            f"• BUILD: <code>{BUILD_MARK}</code>"
        )

    return r


async def _force_single_session(bot: Bot, reason: str, pause: float = 0.6) -> None:
    """
    Жёстко очищает любые предыдущие сессии/хвосты у Telegram:
    1) удаляет вебхук с дропом апдейтов
    2) делает logout() — закрывает ВСЕ старые long-poll соединения
    """
    log.info("🔒 Force single session (%s): delete_webhook + log_out", reason)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        log.warning("delete_webhook failed (%s): %r", reason, e)
    try:
        await bot.log_out()
    except Exception as e:
        # если уже Logged out — это ок
        log.warning("log_out failed (%s): %r", reason, e)
    await asyncio.sleep(pause)


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

    # Префлайт: жёстко гарантируем, что нет вебхука/старых long-poll
    await _force_single_session(bot, reason="preflight")

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
        "app.routers.diag",
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
    dp.include_router(help_router.router);   log.info("✅ router loaded: help")
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

    # Команды, инфо
    await _guard(_set_commands(bot), "set_my_commands")

    me = await bot.get_me()
    token_hash = hashlib.md5(settings.bot_token.encode()).hexdigest()[:8]
    os.environ["BOT_ID"] = str(me.id)  # чтобы diag.api_router мог вернуть его

    log.info("🔑 Token hash: %s", token_hash)
    log.info("🤖 Bot online: @%s (ID: %s)  ENV=%s MODE=%s BUILD=%s",
             me.username, me.id, settings.env, settings.mode, BUILD_MARK)

    # ── Старт polling с автолечением конфликтов ───────────────────────────
    async def _start_polling_once(tag: str) -> None:
        log.info("🚀 Start polling (%s)…", tag)
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])

    try:
        await _start_polling_once("initial")
    except TelegramConflictError as e:
        # первое же столкновение — чистим сессию и повторяем один раз
        log.error("⚠️ TelegramConflictError (initial): %s", e)
        await _force_single_session(bot, reason="conflict-retry", pause=1.0)
        await _start_polling_once("retry")
    # иные исключения пусть валятся вверх — это справедливо для наблюдаемости


# ─────────────────────────── Web mode (FastAPI) ───────────────────────────
def run_web() -> FastAPI:
    app = FastAPI(title="Elaya StageCoach", version=BUILD_MARK)

    @app.get("/status_json")
    async def status_json():
        return await _get_status_dict()

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
