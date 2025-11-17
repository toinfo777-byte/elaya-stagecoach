from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Update

from fastapi import FastAPI, Request

from app.config import settings
from app.routers import router as main_router


# --- bot / dispatcher ---

bot = Bot(
    token=settings.TG_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
)

dp = Dispatcher()
# один корневой роутер, внутри уже подключены start / reviews / training
dp.include_router(main_router)


# --- ASGI-приложение для Render (uvicorn ищет переменную "app") ---

app = FastAPI()


@app.post("/tg/webhook")
async def telegram_webhook(request: Request):
    """
    Точка входа для Telegram webhook.
    Render запускает uvicorn app.bot.main:app,
    поэтому главное — чтобы здесь была переменная `app`.
    """
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot=bot, update=update)
    return {"ok": True}
