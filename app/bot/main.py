from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.config import settings
from app.routers import start_router, reviews_router, training_router

bot = Bot(
    token=settings.TG_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
)

dp = Dispatcher()

# Каждый router включаем только один раз
dp.include_router(start_router)
dp.include_router(training_router)
dp.include_router(reviews_router)
