# app/bot/main.py

import logging

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update, BotCommand

from app.config import settings
from app.routers.start import router as start_router
from app.routers.reviews import router as reviews_router

logger = logging.getLogger(__name__)

# --- aiogram ядро ---

bot = Bot(
    token=settings.TG_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
)

dp = Dispatcher(storage=MemoryStorage())
dp.include_router(start_router)
dp.include_router(reviews_router)

# --- FastAPI приложение для Render ---

app = FastAPI()


@app.on_event("startup")
async def on_startup() -> None:
    """
    Вызывается при старте uvicorn.
    Здесь настраиваем /команды бота.
    """
    commands = [
        BotCommand(command="start", description="Запуск тренера сцены"),
        BotCommand(command="training", description="🎯 Тренировка дня"),
        BotCommand(command="progress", description="📈 Мой прогресс"),
        BotCommand(command="help", description="💬 Помощь"),
        BotCommand(command="policy", description="🔐 Политика"),
        BotCommand(command="pro", description="⭐️ Расширенная версия"),
    ]
    await bot.set_my_commands(commands)
    logger.info("Trainer bot started, commands set.")


@app.post("/tg/webhook")
async def telegram_webhook(request: Request):
    """
    Точка входа для webhook от Telegram.
    Render уже шлёт POST сюда: /tg/webhook
    """
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.get("/healthz")
async def healthz():
    """
    Healthcheck для Render.
    """
    return {"ok": True}
