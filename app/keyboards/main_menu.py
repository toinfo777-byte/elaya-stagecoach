# app/keyboards/main_menu.py
from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- Кнопки главного меню ---

BTN_TRAINING = KeyboardButton(text="📚 Тренировка дня")
BTN_PROGRESS = KeyboardButton(text="📈 Мой прогресс")
BTN_HELP = KeyboardButton(text="💬 Помощь")
BTN_FEEDBACK = KeyboardButton(text="📝 Отзыв о тренировке")
BTN_POLICY = KeyboardButton(text="🔐 Политика")
BTN_PREMIUM = KeyboardButton(text="⭐️ Расширенная версия")

# --- Главное меню тренера ---

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [BTN_TRAINING],
        [BTN_PROGRESS, BTN_HELP],
        [BTN_FEEDBACK],
        [BTN_POLICY, BTN_PREMIUM],
    ],
    resize_keyboard=True,
)
