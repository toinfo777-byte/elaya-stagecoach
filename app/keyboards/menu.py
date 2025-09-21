# app/keyboards/menu.py
from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand

# Тексты кнопок
BTN_TRAINING   = "🎯 Тренировка дня"
BTN_LEADER     = "🧭 Путь лидера"
BTN_POLICY     = "🔐 Политика"
BTN_SETTINGS   = "⚙️ Настройки"

BTN_PROGRESS   = "📈 Мой прогресс"
BTN_CASTING    = "🎭 Мини-кастинг"
BTN_HELP       = "💬 Помощь"
BTN_PREMIUM    = "⭐ Расширенная версия"

# Шорткаты (маленькое меню)
BTN_TO_MENU    = "🏠 В меню"
BTN_TO_SETTINGS= "⚙️ Настройки"
BTN_WIPE       = "🗑 Удалить профиль"


def main_menu() -> ReplyKeyboardMarkup:
    # 4 строки по 2 кнопки — как на твоих скриншотах
    rows = [
        [KeyboardButton(text=BTN_TRAINING), KeyboardButton(text=BTN_PROGRESS)],
        [KeyboardButton(text=BTN_LEADER),   KeyboardButton(text=BTN_CASTING)],
        [KeyboardButton(text=BTN_POLICY),   KeyboardButton(text=BTN_HELP)],
        [KeyboardButton(text=BTN_SETTINGS), KeyboardButton(text=BTN_PREMIUM)],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def small_menu() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=BTN_TO_MENU)],
        [KeyboardButton(text=BTN_TO_SETTINGS)],
        [KeyboardButton(text=BTN_WIPE)],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


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
