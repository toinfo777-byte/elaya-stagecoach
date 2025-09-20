from __future__ import annotations
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand

# ЕДИНЫЕ ТЕКСТЫ КНОПОК
BTN_TRAIN     = "🎯 Тренировка дня"
BTN_PROGRESS  = "📈 Мой прогресс"
BTN_APPLY     = "🧭 Путь лидера"
BTN_CASTING   = "🎭 Мини-кастинг"
BTN_PRIVACY   = "🔐 Политика"
BTN_HELP      = "💬 Помощь"
BTN_PREMIUM   = "⭐️ Расширенная версия"
BTN_SETTINGS  = "⚙️ Настройки"

def main_menu() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=BTN_TRAIN),    KeyboardButton(text=BTN_PROGRESS)],
        [KeyboardButton(text=BTN_APPLY),    KeyboardButton(text=BTN_CASTING)],
        [KeyboardButton(text=BTN_PRIVACY),  KeyboardButton(text=BTN_HELP)],
        [KeyboardButton(text=BTN_PREMIUM),  KeyboardButton(text=BTN_SETTINGS)],
    ]
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        is_persistent=True
    )

def get_bot_commands() -> list[BotCommand]:
    return [
        BotCommand(command="start",    description="Начать / онбординг"),
        BotCommand(command="menu",     description="Открыть меню"),
        BotCommand(command="training", description="Тренировка дня"),
        BotCommand(command="progress", description="Мой прогресс"),
        BotCommand(command="apply",    description="Путь лидера (заявка)"),
        BotCommand(command="casting",  description="Мини-кастинг"),
        BotCommand(command="privacy",  description="Политика конфиденциальности"),
        BotCommand(command="help",     description="Помощь"),
        BotCommand(command="premium",  description="Расширенная версия"),
        BotCommand(command="settings", description="Настройки"),
    ]
