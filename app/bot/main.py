# app/bot/main.py
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.routers import start, training, help, policy, progress, reviews  # ← добавили reviews

bot = Bot(token=settings.TG_BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())

# регистрируем все роутеры
dp.include_router(start.router)
dp.include_router(training.router)
dp.include_router(help.router)
dp.include_router(policy.router)
dp.include_router(progress.router)
dp.include_router(reviews.router)  # ← ВАЖНАЯ СТРОКА
