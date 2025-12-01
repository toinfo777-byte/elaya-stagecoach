from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎭 Тренировка дня")],
        [
            KeyboardButton(text="📈 Мой прогресс"),
            KeyboardButton(text="💬 Помощь"),
        ],
        [
            KeyboardButton(text="🔐 Политика"),
            KeyboardButton(text="⭐️ Расширенная версия"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери, с чего начнём…",
)
