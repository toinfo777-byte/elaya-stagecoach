from __future__ import annotations

import asyncio
import os
import time
from typing import Optional

from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ---- конфиг (минимум, чтобы файл был самодостаточным) ----
class Settings:
    mode: str = os.getenv("MODE", "worker").lower()      # worker | web
    env: str = os.getenv("ENV", "develop")
    tg_bot_token: Optional[str] = os.getenv("TG_BOT_TOKEN")

settings = Settings()

# ---- FastAPI (web) ----
app = FastAPI(title="Elaya StageCoach", version="1.0.0")
_started_at = time.time()

@app.get("/healthz")
def healthz():
    return {"ok": True, "mode": settings.mode, "uptime_s": int(time.time() - _started_at)}

# ---- Aiogram (bot) ----
bot: Optional[Bot] = None
dp: Optional[Dispatcher] = None

def build_bot():
    global bot, dp
    if bot and dp:
        return bot, dp
    if not settings.tg_bot_token:
        raise RuntimeError("TG_BOT_TOKEN is not set")

    bot = Bot(
        token=settings.tg_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Роутеры
    from app.routers import hq as hq_router
    dp.include_router(hq_router.router)

    return bot, dp

async def start_polling():
    b, d = build_bot()
    # снимаем возможный webhook, чтобы не ловить конфликт
    try:
        await b.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass
    await d.start_polling(b)

# ---- entrypoints ----
def _run_worker():
    asyncio.run(start_polling())

# Render/uvicorn подхватит `app` в режиме web.
# В режиме worker запускаем polling немедленно.
if settings.mode == "worker":
    _run_worker()
