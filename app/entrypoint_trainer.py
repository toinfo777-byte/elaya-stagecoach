# app/entrypoint_trainer.py
from __future__ import annotations

from fastapi import FastAPI, Request, Response
from aiogram import Bot, Dispatcher

from app.config import settings

app = FastAPI(title="Elaya Trainer — webhook")
dp = Dispatcher()
bot = Bot(token=... )

@app.post("/tg/webhook")
async def tg_webhook(request: Request) -> Response:
    # никакой авто-рассылки "Webhook alert" здесь
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return Response(status_code=200)
