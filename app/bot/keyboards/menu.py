from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types.bot_command import BotCommand


# ---------- Главная клавиатура ----------
def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Тренировка дня"), KeyboardButton(text="📈 Мой прогресс")],
            [KeyboardButton(text="🧭 Путь лидера"), KeyboardButton(text="🎬 Мини-кастинг")],
            [KeyboardButton(text="🛡 Политика"), KeyboardButton(text="❓ Помощь")],
            [KeyboardButton(text="⭐ Расширенная версия"), KeyboardButton(text="⚙️ Настройки")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


# ---------- Клавиатура раздела Премиума ----------
def premium_kb(has_application: bool) -> ReplyKeyboardMarkup:
    row1 = [KeyboardButton(text="🔎 Что внутри")]
    if has_application:
        row2 = [KeyboardButton(text="📂 Мои заявки")]
    else:
        row2 = [KeyboardButton(text="📝 Оставить заявку")]
    row3 = [KeyboardButton(text="📎 В меню")]

    return ReplyKeyboardMarkup(
        keyboard=[row1, row2, row3],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


# ---------- Команды бота (маленькое /меню Telegram) ----------
def get_bot_commands() -> list[BotCommand]:
    return [
        BotCommand(command="start", description="Начать / онбординг"),
        BotCommand(command="menu", description="Открыть меню"),
        BotCommand(command="training", description="Тренировка дня"),
        BotCommand(command="progress", description="Мой прогресс"),
        BotCommand(command="apply", description="Путь лидера (заявка)"),
        BotCommand(command="casting", description="Мини-кастинг"),
        BotCommand(command="privacy", description="Политика конфиденциальности"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="premium", description="Расширенная версия"),
        BotCommand(command="settings", description="Настройки"),
    ]
