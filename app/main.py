from __future__ import annotations
import os, asyncio, logging
from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.routers import hq as hq_router

log = logging.getLogger("elaya.main")
logging.basicConfig(level=logging.INFO)

MODE = os.getenv("MODE", "web").lower()
ENV = os.getenv("ENV", "staging")

app = FastAPI(title="Elaya Stagecoach Web", version="1.0.0")
app.include_router(hq_router.router)  # /healthz и /render

async def start_bot() -> None:
    token = os.getenv("TG_BOT_TOKEN", "").strip()
    if not token:
        log.error("TG_BOT_TOKEN is empty — bot won't start.")
        return
    dp = Dispatcher()
    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    log.info("Start polling… ENV=%s", ENV)
    await dp.start_polling(bot)

def start_web() -> None:
    # Render сам выставляет PORT
    import uvicorn
    port = int(os.getenv("PORT", "10000"))
    log.info("Start web mode on port=%s ENV=%s", port, ENV)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    if MODE == "worker":
        asyncio.run(start_bot())
    else:
        start_web()
