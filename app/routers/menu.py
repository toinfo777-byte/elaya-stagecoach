# app/routers/menu.py
from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Единые тексты кнопок (экспортируем наружу)
BTN_TRAIN    = "🎯 Тренировка дня"
BTN_PROGRESS = "📈 Мой прогресс"
BTN_APPLY    = "🧭 Путь лидера"
BTN_CASTING  = "🎭 Мини-кастинг"
BTN_PRIVACY  = "🔐 Политика"
BTN_HELP     = "💬 Помощь"


def main_menu() -> ReplyKeyboardMarkup:
    """
    Основное меню. Строгий, стабильный порядок.
    """
    kb = [
        [KeyboardButton(text=BTN_TRAIN),    KeyboardButton(text=BTN_PROGRESS)],
        [KeyboardButton(text=BTN_APPLY),    KeyboardButton(text=BTN_CASTING)],
        [KeyboardButton(text=BTN_PRIVACY),  KeyboardButton(text=BTN_HELP)],
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Меню",
    )
