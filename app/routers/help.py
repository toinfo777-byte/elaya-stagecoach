from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

help_router = Router(name="help")


# === Keyboards ===============================================================

def _menu_kb() -> InlineKeyboardMarkup:
    # go:* ловит entrypoints.go-роутер
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏋️ Тренировка дня", callback_data="go:training")],
        [InlineKeyboardButton(text="🎭 Мини-кастинг",   callback_data="go:casting")],
        [InlineKeyboardButton(text="🧭 Путь лидера",    callback_data="go:leader")],
        [InlineKeyboardButton(text="📈 Мой прогресс",   callback_data="go:progress")],
        [InlineKeyboardButton(text="💬 Помощь / FAQ",   callback_data="go:help")],
        [InlineKeyboardButton(text="🔐 Политика",       callback_data="go:privacy")],
        [InlineKeyboardButton(text="⚙️ Настройки",      callback_data="go:settings")],
        [InlineKeyboardButton(text="⭐ Расширенная версия", callback_data="go:extended")],
    ])


def _back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")]
    ])


def _settings_kb() -> InlineKeyboardMarkup:
    # Кнопки согласованы с routers/settings.py
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В меню",          callback_data="settings:menu")],
        [InlineKeyboardButton(text="🗑 Удалить профиль", callback_data="settings:delete")],
    ])


# === Helpers =================================================================

async def _reply(obj: Message | CallbackQuery, text: str,
                 kb: InlineKeyboardMarkup | None = None):
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        return await obj.message.answer(text, reply_markup=kb)
    return await obj.answer(text, reply_markup=kb)


# === Public API (используется в entrypoints.py и др.) ========================

async def show_main_menu(obj: Message | CallbackQuery):
    text = (
        "Команды и разделы: выбери нужное ⤵️\n\n"
        "🏋️ Тренировка дня — ежедневная рутина 5–15 мин.\n"
        "🎭 Мини-кастинг — быстрый чек 2–3 мин.\n"
        "🧭 Путь лидера — цель + микро-задание + заявка.\n"
        "📈 Мой прогресс — стрик и эпизоды за 7 дней.\n"
        "💬 Помощь / FAQ — ответы на частые вопросы.\n"
        "⚙️ Настройки — профиль.\n"
        "🔐 Политика — как храним и используем ваши данные."
    )
    await _reply(obj, text, _menu_kb())


async def show_privacy(obj: Message | CallbackQuery):
    text = (
        "🔐 Политика конфиденциальности\n\n"
        "Мы бережно храним ваши данные и используем их только "
        "для работы бота и улучшения сервиса."
    )
    await _reply(obj, text, _back_kb())


async def show_settings(obj: Message | CallbackQuery):
    text = "⚙️ Настройки. Можешь удалить профиль или вернуться в меню."
    await _reply(obj, text, _settings_kb())


# === Local handlers (только /help команда показывает главное меню) ===========

@help_router.message(Command("help"))
async def cmd_help(m: Message):
    await show_main_menu(m)


__all__ = ["help_router", "show_main_menu", "show_privacy", "show_settings"]
