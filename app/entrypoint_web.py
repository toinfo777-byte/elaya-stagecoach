# app/entrypoint_web.py
from __future__ import annotations

from fastapi import FastAPI, Request, Response
from aiogram import Bot, Dispatcher

from app.config import settings

app = FastAPI(title="Elaya Stagecoach — webhook")
dp = Dispatcher()
bot = Bot(token=... )  # как у тебя уже подключено

# Раньше вы могли слать сюда алёрт "Webhook online; worker may be stopped."
# Больше этого не делаем, чтобы не плодить дубли.
@app.post("/tg/webhook")
async def tg_webhook(request: Request) -> Response:
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return Response(status_code=200)
