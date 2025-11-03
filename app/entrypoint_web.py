from __future__ import annotations

import logging
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update

from app.config import settings
from app.build import BUILD_MARK, BUILD_SHA
from app.routers import hq_status

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
log = logging.getLogger("elaya.web")

# --- aiogram core
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()
dp.include_router(hq_status.router)

# --- fastapi app
app = FastAPI(title="Elaya StageCoach Webhook")

@app.get("/healthz", response_class=PlainTextResponse)
async def healthz():
    return "OK"

@app.get("/")
async def root():
    return {
        "service": "elaya-stagecoach-web",
        "env": settings.ENV,
        "mode": settings.MODE,
        "build": BUILD_SHA or BUILD_MARK,
    }

@app.post(settings.WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_webhook_update(bot, update)
    return JSONResponse({"ok": True})

async def _ensure_webhook():
    """Ставит/обновляет webhook, если передан PUBLIC_BASE_URL и не выключен AUTO_SET_WEBHOOK."""
    if not settings.PUBLIC_BASE_URL or not settings.AUTO_SET_WEBHOOK:
        log.info("Webhook auto-set disabled or no PUBLIC_BASE_URL")
        return
    url = settings.PUBLIC_BASE_URL.rstrip("/") + settings.WEBHOOK_PATH
    info = await bot.get_webhook_info()
    if info.url != url:
        await bot.set_webhook(url, allowed_updates=["message"])
        log.info("Webhook set: %s", url)
    else:
        log.info("Webhook already set: %s", url)

@app.on_event("startup")
async def on_startup():
    log.info(
        "Starting Elaya web | ENV=%s MODE=%s BUILD=%s",
        settings.ENV, settings.MODE, BUILD_SHA or BUILD_MARK
    )
    await _ensure_webhook()

@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()

# локальный запуск:  python -m app.entrypoint_web
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.entrypoint_web:app", host="0.0.0.0", port=settings.PORT, reload=False)
