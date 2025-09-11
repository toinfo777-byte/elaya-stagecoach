from __future__ import annotations
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Тексты кнопок меню (используются в разных роутерах)
BTN_TRAIN = "🎯 Тренировка дня"
BTN_PROGRESS = "📈 Мой прогресс"
BTN_APPLY = "Путь лидера"
BTN_CASTING = "🎭 Мини-кастинг"
BTN_PRIVACY = "🔐 Политика"
BTN_HELP = "💬 Помощь"
BTN_SETTINGS = "⚙️ Настройки"
BTN_PREMIUM = "⭐ Расширенная версия"
BTN_WIPE = "🗑 Удалить профиль"

def main_menu() -> ReplyKeyboardMarkup:
    """
    Стабильная раскладка:
    1) две широкие
    2) широкая
    3) широкая
    4) пара «узких»
    5) пара «узких»
    6) широкая (удаление профиля)
    """
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text=BTN_TRAIN), KeyboardButton(text=BTN_PROGRESS)],
            [KeyboardButton(text=BTN_APPLY)],
            [KeyboardButton(text=BTN_CASTING)],
            [KeyboardButton(text=BTN_PRIVACY), KeyboardButton(text=BTN_HELP)],
            [KeyboardButton(text=BTN_SETTINGS), KeyboardButton(text=BTN_PREMIUM)],
            [KeyboardButton(text=BTN_WIPE)],
        ],
    )
