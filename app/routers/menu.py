from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ——— Тексты кнопок (используются во всех роутерах) ———
BTN_TRAIN = "🎯 Тренировка дня"
BTN_PROGRESS = "📈 Мой прогресс"
BTN_APPLY = "🧭 Путь лидера"
BTN_CASTING = "🎭 Мини-кастинг"
BTN_HELP = "💬 Помощь"
BTN_PRIVACY = "🔐 Политика"
BTN_SETTINGS = "⚙️ Настройки"
BTN_PREMIUM = "⭐️ Расширенная версия"
BTN_DELETE = "🧹 Удалить профиль"  # если нужно в settings

def main_menu() -> ReplyKeyboardMarkup:
    """
    Стандартное нижнее меню. Всегда одно и то же, не «скачет».
    """
    rows = [
        [KeyboardButton(text=BTN_TRAIN), KeyboardButton(text=BTN_PROGRESS)],
        [KeyboardButton(text=BTN_APPLY), KeyboardButton(text=BTN_CASTING)],
        [KeyboardButton(text=BTN_PRIVACY), KeyboardButton(text=BTN_HELP)],
        [KeyboardButton(text=BTN_PREMIUM), KeyboardButton(text=BTN_SETTINGS)],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
