from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext

help_router = Router(name="help")


# ---------- UI ----------
def _menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏋️ Тренировка дня",   callback_data="go:training")],
        [InlineKeyboardButton(text="🎭 Мини-кастинг",     callback_data="go:casting")],
        [InlineKeyboardButton(text="🧭 Путь лидера",      callback_data="go:leader")],
        [InlineKeyboardButton(text="📈 Мой прогресс",     callback_data="go:progress")],
        [InlineKeyboardButton(text="🔐 Политика",         callback_data="go:privacy")],
        [InlineKeyboardButton(text="⚙️ Настройки",        callback_data="go:settings")],
    ])

def _back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])

def _settings_kb() -> InlineKeyboardMarkup:
    # ВАЖНО: callback_data на удаление профиля совпадает с твоим settings-роутером: "settings:delete"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В меню",         callback_data="go:menu")],
        [InlineKeyboardButton(text="🗑 Удалить профиль", callback_data="settings:delete")],
    ])


# ---------- универсальная отправка для Message | CallbackQuery ----------
async def _reply(obj: Message | CallbackQuery, text: str,
                 kb: InlineKeyboardMarkup | None = None):
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        await obj.message.answer(text, reply_markup=kb)
    else:
        await obj.answer(text, reply_markup=kb)


# ---------- ПУБЛИЧНЫЕ ФУНКЦИИ (их импортирует entrypoints.py) ----------
async def show_main_menu(obj: Message | CallbackQuery):
    text = (
        "Команды и разделы: выбери нужное ⤵️\n\n"
        "🏋️ Тренировка дня — ежедневная рутина 5–15 мин.\n"
        "🎭 Мини-кастинг — быстрый чек 2–3 мин.\n"
        "🧭 Путь лидера — цель + микро-задание + заявка.\n"
        "📈 Мой прогресс — стрик и эпизоды за 7 дней.\n"
        "⚙️ Настройки — профиль.\n"
        "🔐 Политика — как храним и используем ваши данные."
    )
    await _reply(obj, text, _menu_kb())


async def show_privacy(obj: Message | CallbackQuery):
    # Можешь заменить текст на свой PRIVACY_TEXT из privacy.py по желанию
    text = (
        "🔐 Политика конфиденциальности\n\n"
        "Мы бережно храним ваши данные и используем их только для работы бота "
        "и улучшения качества тренировок."
    )
    await _reply(obj, text, _back_kb())


async def show_settings(obj: Message | CallbackQuery, state: FSMContext | None = None):
    # state тут опционален: entrypoints может передавать его, но мы не обязаны очищать
    text = "⚙️ Настройки. Можешь удалить профиль или вернуться в меню."
    await _reply(obj, text, _settings_kb())


# ---------- собственные хэндлеры раздела «Помощь» ----------
@help_router.message(Command("help"))
@help_router.message(F.text == "💬 Помощь")
async def help_cmd(m: Message):
    await show_main_menu(m)

@help_router.callback_query(F.data == "go:menu")
async def cb_menu(cb: CallbackQuery):
    await show_main_menu(cb)

@help_router.callback_query(F.data == "go:privacy")
async def cb_privacy(cb: CallbackQuery):
    await show_privacy(cb)

@help_router.callback_query(F.data == "go:settings")
async def cb_settings(cb: CallbackQuery):
    await show_settings(cb)


__all__ = ["help_router", "show_main_menu", "show_privacy", "show_settings"]
