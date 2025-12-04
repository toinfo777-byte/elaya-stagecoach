from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Главное меню тренера
MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎭 Тренировка дня")],
        [
            KeyboardButton(text="📈 Мой прогресс"),
            KeyboardButton(text="💬 Помощь"),
        ],
        [KeyboardButton(text="⭐ Расширенная версия")],
    ],
    resize_keyboard=True,
)
