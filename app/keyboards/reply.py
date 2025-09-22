# app/keyboards/reply.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# === ТЕКУЩИЕ КОНСТАНТЫ КНОПОК (ваша версия) =======================
BTN_TRAINING = "🏋️ Тренировка дня"
BTN_PROGRESS = "📈 Мой прогресс"
BTN_CASTING  = "🎭 Мини-кастинг"
BTN_APPLY    = "🧭 Путь лидера"
BTN_HELP     = "💬 Помощь"
BTN_POLICY   = "🔐 Политика"              # текущее имя
BTN_SETTINGS = "⚙️ Настройки"
BTN_EXTENDED = "⭐ Расширенная версия"

BTN_MENU   = "🏠 В меню"
BTN_DELETE = "🗑 Удалить профиль"


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_TRAINING), KeyboardButton(text=BTN_PROGRESS)],
            [KeyboardButton(text=BTN_APPLY),    KeyboardButton(text=BTN_CASTING)],
            [KeyboardButton(text=BTN_POLICY),   KeyboardButton(text=BTN_HELP)],
            [KeyboardButton(text=BTN_SETTINGS), KeyboardButton(text=BTN_EXTENDED)],
        ],
        resize_keyboard=True
    )


def settings_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_MENU)],
            [KeyboardButton(text=BTN_SETTINGS), KeyboardButton(text=BTN_DELETE)],
        ],
        resize_keyboard=True
    )


# === ОБРАТНАЯ СОВМЕСТИМОСТЬ (алиасы под старый публичный API) ====
# Роутеры ждут main_menu_kb(), settings_kb() и BTN_PRIVACY.
main_menu_kb = main_menu
settings_kb  = settings_menu
BTN_PRIVACY  = BTN_POLICY

__all__ = [
    # новые имена
    "main_menu", "settings_menu",
    "BTN_TRAINING", "BTN_PROGRESS", "BTN_CASTING", "BTN_APPLY",
    "BTN_HELP", "BTN_POLICY", "BTN_SETTINGS", "BTN_EXTENDED",
    "BTN_MENU", "BTN_DELETE",

    # алиасы для совместимости
    "main_menu_kb", "settings_kb", "BTN_PRIVACY",
]
