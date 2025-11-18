from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update

from fastapi import FastAPI

from app.config import settings
from app.routers import router as main_router


# --- aiogram: бот и диспетчер ---

bot = Bot(
    token=settings.TG_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
)

dp = Dispatcher(storage=MemoryStorage())
dp.include_router(main_router)


# --- ASGI-приложение для Render / uvicorn ---

app = FastAPI()


@app.get("/healthz")
async def healthcheck() -> dict:
    return {"status": "ok"}


@app.post("/tg/webhook")
async def tg_webhook(update: dict) -> dict:
    telegram_update = Update(**update)
    await dp.feed_update(bot, telegram_update)
    return {"ok": True}
