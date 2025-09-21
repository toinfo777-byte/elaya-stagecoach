from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Основные кнопки
BTN_TRAINING = "🎯 Тренировка дня"
BTN_LEADER   = "🧭 Путь лидера"
BTN_POLICY   = "🔐 Политика"
BTN_SETTINGS = "⚙️ Настройки"

BTN_PROGRESS = "📈 Мой прогресс"
BTN_CASTING  = "🎭 Мини-кастинг"
BTN_HELP     = "💬 Помощь"
BTN_PREMIUM  = "⭐️ Расширенная версия"

# Шорткаты
BTN_TO_MENU      = "🏠 В меню"
BTN_TO_SETTINGS  = "⚙️ Настройки"
BTN_WIPE         = "🗑 Удалить профиль"


def main_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text=BTN_TRAINING), KeyboardButton(text=BTN_PROGRESS)],
        [KeyboardButton(text=BTN_LEADER),   KeyboardButton(text=BTN_CASTING)],
        [KeyboardButton(text=BTN_POLICY),   KeyboardButton(text=BTN_HELP)],
        [KeyboardButton(text=BTN_SETTINGS), KeyboardButton(text=BTN_PREMIUM)],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Меню")


def small_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text=BTN_TO_MENU)],
        [KeyboardButton(text=BTN_TO_SETTINGS), KeyboardButton(text=BTN_WIPE)],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
