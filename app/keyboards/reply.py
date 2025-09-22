# app/keyboards/reply.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BTN_TRAINING = "🏋️ Тренировка дня"
BTN_PROGRESS = "📈 Мой прогресс"
BTN_CASTING  = "🎭 Мини-кастинг"
BTN_APPLY    = "🧭 Путь лидера"
BTN_HELP     = "💬 Помощь"
BTN_POLICY   = "🔐 Политика"
BTN_SETTINGS = "⚙️ Настройки"
BTN_EXTENDED = "⭐ Расширенная версия"

BTN_MENU   = "🏠 В меню"
BTN_DELETE = "🗑 Удалить профиль"

def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_TRAINING), KeyboardButton(text=BTN_PROGRESS)],
            [KeyboardButton(text=BTN_APPLY),    KeyboardButton(text=BTN_CASTING)],
            [KeyboardButton(text=BTN_POLICY),   KeyboardButton(text=BTN_HELP)],
            [KeyboardButton(text=BTN_SETTINGS), KeyboardButton(text=BTN_EXTENDED)],
        ],
        resize_keyboard=True
    )

# для совместимости с твоими импортами из разных мест:
main_menu = main_menu_kb

def settings_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_MENU)],
            [KeyboardButton(text=BTN_SETTINGS), KeyboardButton(text=BTN_DELETE)],
        ],
        resize_keyboard=True
    )

settings_menu = settings_kb
BTN_PRIVACY  = BTN_POLICY

__all__ = [
    "main_menu_kb", "settings_kb",
    "main_menu", "settings_menu",
    "BTN_TRAINING", "BTN_PROGRESS", "BTN_CASTING", "BTN_APPLY",
    "BTN_HELP", "BTN_POLICY", "BTN_SETTINGS", "BTN_EXTENDED",
    "BTN_MENU", "BTN_DELETE",
    "BTN_PRIVACY",
]
