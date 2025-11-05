from __future__ import annotations

import logging
import os
from typing import Optional

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import PlainTextResponse, JSONResponse

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update

from app.config import settings
from app.build import BUILD_MARK

# --------------------------
# Логирование
# --------------------------
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("elaya.main")

# --------------------------
# FastAPI + aiogram init
# --------------------------
app = FastAPI(title="Elaya StageCoach", version="1.0")

bot: Optional[Bot] = None
dp: Optional[Dispatcher] = None

BASE_URL = os.getenv("STAGECOACH_WEB_URL")
WEBHOOK_PATH = "/tg/webhook"
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}" if BASE_URL else None


def _safe_include(path: str):
    """Безопасное подключение роутеров"""
    global dp
    if not dp:
        return
    try:
        module = __import__(path, fromlist=["router"])
        router = getattr(module, "router", None)
        if router:
            dp.include_router(router)
            log.info(f"router loaded: {path}")
    except Exception as e:
        log.warning(f"skip {path}: {e}")


def include_profile_routers():
    if not dp:
        return
    _safe_include("app.routers.system")
    if settings.BOT_PROFILE == "hq":
        _safe_include("app.routers.hq")
    else:
        _safe_include("app.routers.menu")
        _safe_include("app.routers.training")
        _safe_include("app.routers.progress")


@app.on_event("startup")
async def on_startup():
    global bot, dp
    if not (settings.TELEGRAM_TOKEN or settings.BOT_TOKEN or settings.TG_BOT_TOKEN):
        log.error("No TELEGRAM_TOKEN found — bot disabled")
        return

    token = settings.TELEGRAM_TOKEN or settings.BOT_TOKEN or settings.TG_BOT_TOKEN
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    include_profile_routers()

    if WEBHOOK_URL:
        await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True, allowed_updates=["message"])
        me = await bot.get_me()
        log.info(f"Webhook set for @{me.username} ({settings.BOT_PROFILE}) → {WEBHOOK_URL}")
    else:
        log.warning("STAGECOACH_WEB_URL not set — webhook disabled")

    log.info(f"Startup complete | profile={settings.BOT_PROFILE} | build={BUILD_MARK}")


@app.on_event("shutdown")
async def on_shutdown():
    global bot
    if bot:
        try:
            await bot.delete_webhook(drop_pending_updates=False)
        except Exception:
            pass
        await bot.session.close()
        bot = None
    log.info("Shutdown complete and client session closed.")


# --------------------------
# Endpoints
# --------------------------
@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Elaya StageCoach web is alive."


@app.get("/healthz", response_class=PlainTextResponse)
async def healthz():
    return "ok"


@app.get("/build")
async def build():
    return JSONResponse({"build": BUILD_MARK, "profile": settings.BOT_PROFILE})


@app.post(WEBHOOK_PATH)
async def tg_webhook(request: Request) -> Response:
    global bot, dp
    if not bot or not dp:
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        data = await request.json()
        update = Update.model_validate(data)
        await dp.feed_update(bot, update)
    except Exception as e:
        log.exception(f"update error: {e}")
    return Response(status_code=status.HTTP_200_OK)
