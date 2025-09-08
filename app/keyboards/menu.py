# app/keyboards/menu.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎯 Тренировка дня"), KeyboardButton(text="📈 Мой прогресс")],
            [KeyboardButton(text="Путь лидера")],   # <-- НОВОЕ
            [KeyboardButton(text="🎭 Мини-кастинг")],
            [KeyboardButton(text="🔐 Политика"), KeyboardButton(text="💬 Помощь")],
            [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="⭐ Расширенная версия")],
            [KeyboardButton(text="🗑 Удалить профиль")],  # NEW (как у тебя в коде)
        ],
        resize_keyboard=True
    )
