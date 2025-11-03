# app/main.py
from __future__ import annotations

import os
import asyncio
import logging
import random
from typing import Optional

from fastapi import FastAPI, Request, Header, HTTPException
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramConflictError
from aiogram.types import Update

from app.config import settings
from app.build import BUILD_MARK

dp: Optional[Dispatcher] = None
bot: Optional[Bot] = None

# ---------- Логи ----------
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("elaya.main")

# ---------- FastAPI ----------
app = FastAPI(title="Elaya StageCoach", version=BUILD_MARK)

@app.get("/healthz")
async def healthz():
    loop = asyncio.get_event_loop()
    return {"ok": True, "uptime_s": int(loop.time())}


# ---------- Профильные роутеры ----------
def _include_routers_for_profile(_dp: Dispatcher, profile: str) -> None:
    from app.routers import system, hq
    # временный дебаг (можно убрать)
    try:
        from app.routers import debug
        _dp.include_router(debug.router)
    except Exception as e:
        logger.warning("debug router not loaded: %s", e)
    _dp.include_router(system.router)
    _dp.include_router(hq.router)

    profile = (profile or "hq").lower()
    if profile == "trainer":
        from app.routers import (
            help as help_router,
            cmd_aliases,
            onboarding,
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
        )
        _dp.include_router(help_router.router)
        _dp.include_router(cmd_aliases.router)
        _dp.include_router(onboarding.router)
        _dp.include_router(minicasting.router)
        _dp.include_router(leader.router)
        _dp.include_router(training.router)
        _dp.include_router(progress.router)
        _dp.include_router(privacy.router)
        _dp.include_router(settings_mod.router)
        _dp.include_router(extended.router)
        _dp.include_router(casting.router)
        _dp.include_router(apply.router)
        _dp.include_router(faq.router)
        _dp.include_router(devops_sync.router)
        _dp.include_router(panic.router)
    elif profile == "web":
        pass
    else:
        pass


# ---------- WEBHOOK-МОД (MODE=web) ----------
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/tg/webhook")
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE", "")          # например: https://elaya-stagecoach-web.onrender.com
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")      # любая длинная строка

async def _web_startup():
    """
    Инициализация бота/диспетчера и установка webhook.
    """
    global dp, bot
    assert WEBHOOK_BASE, "WEBHOOK_BASE is required in MODE=web"
    assert WEBHOOK_SECRET, "WEBHOOK_SECRET is required in MODE=web"

    bot = Bot(
        token=settings.TG_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    profile = os.getenv("BOT_PROFILE", "hq")
    logger.info("WEB: Launching with BOT_PROFILE=%s", profile)
    _include_routers_for_profile(dp, profile)

    used = dp.resolve_used_update_types()
    logger.info("WEB: allowed_updates=%s", used)

    full_url = f"{WEBHOOK_BASE.rstrip('/')}{WEBHOOK_PATH}"
    # Снимем старый, на всякий
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except TelegramBadRequest:
        pass

    # Ставим новый вебхук с секретом (Telegram будет присылать заголовок)
    await bot.set_webhook(url=full_url, secret_token=WEBHOOK_SECRET)
    logger.info("Webhook set: %s", full_url)


@app.on_event("startup")
async def _on_startup():
    if settings.MODE.lower() == "web":
        await _web_startup()


@app.on_event("shutdown")
async def _on_shutdown():
    global dp, bot
    if bot:
        try:
            await bot.delete_webhook(drop_pending_updates=False)
        except TelegramBadRequest:
            pass
    if dp:
        await dp.storage.close()
    if bot:
        await bot.session.close()


@app.post(WEBHOOK_PATH)
async def tg_webhook(request: Request, x_telegram_bot_api_secret_token: str = Header(None)):
    """
    Точка входа для Telegram. Проверяем секрет, парсим Update и отдаём в aiogram.
    """
    if not WEBHOOK_SECRET or x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="forbidden")
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}


# ---------- POLLING-МОД (MODE=worker) ----------
async def start_polling() -> None:
    """
    Конфликто-устойчивый polling (если понадобится оставить).
    """
    global dp, bot

    startup_delay = int(os.getenv("STARTUP_DELAY", "0"))
    if startup_delay > 0:
        logger.info("Startup delay: %s sec (to avoid overlap)", startup_delay)
        await asyncio.sleep(startup_delay)

    bot = Bot(
        token=settings.TG_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    max_conflict_seconds = int(os.getenv("CONFLICT_TIMEOUT", "120"))
    started_at = asyncio.get_event_loop().time()

    try:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Webhook deleted (drop_pending_updates=True).")
        except TelegramBadRequest as e:
            logger.warning("delete_webhook: %s (ignored)", e)

        dp = Dispatcher()
        profile = os.getenv("BOT_PROFILE", "hq")
        logger.info("WORKER: Launching with BOT_PROFILE=%s", profile)
        _include_routers_for_profile(dp, profile)

        used = dp.resolve_used_update_types()
        logger.info("WORKER: allowed_updates=%s", used)

        attempt = 0
        while True:
            try:
                await dp.start_polling(bot, allowed_updates=used)
                break
            except TelegramConflictError as e:
                elapsed = asyncio.get_event_loop().time() - started_at
                attempt += 1
                if elapsed >= max_conflict_seconds:
                    logger.error("Conflict persists > %ss, giving up. %s", max_conflict_seconds, e)
                    raise
                backoff = min(5.0 + attempt * 0.5, 10.0) + random.uniform(0, 1.5)
                logger.warning(
                    "Conflict (attempt=%s, elapsed=%.1fs). Sleep %.2fs and retry...",
                    attempt, elapsed, backoff
                )
                await asyncio.sleep(backoff)
    finally:
        if dp:
            await dp.storage.close()
        if bot:
            await bot.session.close()


# ---------- Точка входа ----------
def run_app():
    mode = settings.MODE.lower()
    if mode == "web":
        logger.info("Starting WEB app... ENV=%s MODE=web BUILD=%s", settings.ENV, BUILD_MARK)
        return app
    elif mode == "worker":
        logger.info("Starting BOT polling... ENV=%s MODE=worker BUILD=%s", settings.ENV, BUILD_MARK)
        asyncio.run(start_polling())
    else:
        raise RuntimeError(f"Unknown MODE={settings.MODE!r}")


if __name__ == "__main__":
    run_app()
