# app/keyboards/menu.py
from __future__ import annotations

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BotCommand,
)

# Тексты кнопок (основные)
BTN_TRAINING   = "🎯 Тренировка дня"
BTN_PROGRESS   = "📈 Мой прогресс"
BTN_LEADER     = "🧭 Путь лидера"
BTN_CASTING    = "🎭 Мини-кастинг"
BTN_POLICY     = "🔐 Политика"
BTN_HELP       = "💬 Помощь"
BTN_SETTINGS   = "⚙️ Настройки"
BTN_PREMIUM    = "⭐ Расширенная версия"

# Альтернативные названия / расширенные
BTN_MENU       = "Меню"
BTN_APPLY      = BTN_LEADER
BTN_EXTENDED   = BTN_PREMIUM

# Шорткаты (маленькое меню)
BTN_TO_MENU     = "🏠 В меню"
BTN_TO_SETTINGS = "⚙️ Настройки"
BTN_WIPE        = "🗑 Удалить профиль"


# === Reply Keyboards ===========================================================

def main_menu() -> ReplyKeyboardMarkup:
    """
    Основное меню — 4 строки по 2 кнопки (как на скриншотах).
    """
    rows = [
        [KeyboardButton(text=BTN_TRAINING), KeyboardButton(text=BTN_PROGRESS)],
        [KeyboardButton(text=BTN_LEADER),   KeyboardButton(text=BTN_CASTING)],
        [KeyboardButton(text=BTN_POLICY),   KeyboardButton(text=BTN_HELP)],
        [KeyboardButton(text=BTN_SETTINGS), KeyboardButton(text=BTN_PREMIUM)],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def small_menu() -> ReplyKeyboardMarkup:
    """
    Мини-меню для настроек/удаления профиля.
    """
    rows = [
        [KeyboardButton(text=BTN_TO_MENU)],
        [KeyboardButton(text=BTN_TO_SETTINGS)],
        [KeyboardButton(text=BTN_WIPE)],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


# === Inline Keyboards ==========================================================

def to_menu_inline() -> InlineKeyboardMarkup:
    """
    Кнопка возврата в меню (inline).
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В меню", callback_data="menu:open")]
    ])


# === Bot Commands =============================================================

def get_bot_commands() -> list[BotCommand]:
    # aiogram v3 — ТОЛЬКО именованные аргументы!
    return [
        BotCommand(command="start",    description="Начать / онбординг"),
        BotCommand(command="menu",     description="Открыть меню"),
        BotCommand(command="training", description="Тренировка"),
        BotCommand(command="casting",  description="Мини-кастинг"),
        BotCommand(command="progress", description="Мой прогресс"),
        BotCommand(command="apply",    description="Путь лидера (заявка)"),
        BotCommand(command="privacy",  description="Политика"),
        BotCommand(command="help",     description="Помощь"),
        BotCommand(command="settings", description="Настройки"),
        BotCommand(command="cancel",   description="Отмена"),
    ]
