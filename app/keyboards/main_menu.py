# app/keyboards/main_menu.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏋️‍♂️ Тренировка дня")],
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
    input_field_placeholder="Команды и разделы: выбери нужное ⤵️",
)
