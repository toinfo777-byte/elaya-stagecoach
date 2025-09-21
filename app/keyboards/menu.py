from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand

# — Тексты кнопок (должны в точности совпадать с тем, что присылает клавиатура)
BTN_TRAINING = "🎯 Тренировка дня"
BTN_LEADER = "🧭 Путь лидера"
BTN_PRIVACY = "🔐 Политика"
BTN_SETTINGS = "⚙️ Настройки"
BTN_PROGRESS = "📈 Мой прогресс"
BTN_CASTING = "🎭 Мини-кастинг"
BTN_HELP = "💬 Помощь"
BTN_PREMIUM = "⭐ Расширенная версия"

# reply-shortcuts
BTN_TO_MENU = "🏠 В меню"
BTN_WIPE = "🗑 Удалить профиль"

def main_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text=BTN_TRAINING), KeyboardButton(text=BTN_PROGRESS)],
            [KeyboardButton(text=BTN_LEADER),   KeyboardButton(text=BTN_CASTING)],
            [KeyboardButton(text=BTN_HELP),     KeyboardButton(text=BTN_PREMIUM)],
            [KeyboardButton(text=BTN_PRIVACY),  KeyboardButton(text=BTN_SETTINGS)],
        ],
    )
    return kb

def small_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text=BTN_TO_MENU), KeyboardButton(text=BTN_SETTINGS)],
            [KeyboardButton(text=BTN_WIPE)],
        ],
    )
    return kb

def get_bot_commands() -> list[BotCommand]:
    # Для /help и set_my_commands
    return [
        BotCommand(command="start",    description="Начать / онбординг"),
        BotCommand(command="menu",     description="Открыть меню"),
        BotCommand(command="training", description="Тренировка"),
        BotCommand(command="casting",  description="Мини-кастинг"),
        BotCommand(command="progress", description="Мой прогресс"),
        BotCommand(command="apply",    description="Путь лидера"),
        BotCommand(command="privacy",  description="Политика конфиденциальности"),
        BotCommand(command="help",     description="Помощь"),
        BotCommand(command="settings", description="Настройки"),
        BotCommand(command="cancel",   description="Отмена"),
    ]
