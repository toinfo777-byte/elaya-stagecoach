from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.config import settings
from app.routers import start, reviews, training

bot = Bot(
    token=settings.TG_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
)
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(training.router)   # один раз!
dp.include_router(reviews.router)
