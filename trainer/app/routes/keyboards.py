from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BTN_TRAINING_DAY = "🎭 Тренировка дня"
BTN_PROGRESS = "📈 Мой прогресс"
BTN_HELP = "💬 Помощь"
BTN_PREMIUM = "⭐️ Расширенная версия"


MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_TRAINING_DAY)],
        [KeyboardButton(text=BTN_PROGRESS), KeyboardButton(text=BTN_HELP)],
        [KeyboardButton(text=BTN_PREMIUM)],
    ],
    resize_keyboard=True,
)
