# app/routers/help.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)

router = Router(name="help")

# ---------- UI ----------

def _menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏋️ Тренировка дня", callback_data="go:training")],
        [InlineKeyboardButton(text="🎭 Мини-кастинг",   callback_data="go:casting")],
        [InlineKeyboardButton(text="🧭 Путь лидера",    callback_data="go:leader")],
        [InlineKeyboardButton(text="📈 Мой прогресс",   callback_data="go:progress")],
        [InlineKeyboardButton(text="🔐 Политика",       callback_data="go:privacy")],
        [InlineKeyboardButton(text="⚙️ Настройки",      callback_data="go:settings")],
    ])

def _back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")]
    ])

def _settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Удалить профиль", callback_data="settings:delete_profile")],
        [InlineKeyboardButton(text="🏠 В меню",          callback_data="go:menu")],
    ])

# ---------- универсальная отправка ----------

async def _reply(obj: Message | CallbackQuery, text: str,
                 kb: InlineKeyboardMarkup | None = None):
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        return await obj.message.answer(text, reply_markup=kb)
    return await obj.answer(text, reply_markup=kb)

# ---------- публичные экраны (их импортирует entrypoints.py) ----------

async def show_main_menu(obj: Message | CallbackQuery):
    text = (
        "Команды и разделы: выбери нужное ⤵️\n\n"
        "🏋️ Тренировка дня — ежедневная рутина 5–15 мин.\n"
        "🎭 Мини-кастинг — быстрый чек 2–3 мин.\n"
        "🧭 Путь лидера — цель + микро-задание + заявка.\n"
        "📈 Мой прогресс — стрик и эпизоды за 7 дней.\n"
        "🔐 Политика — как храним и используем ваши данные.\n"
        "⚙️ Настройки — профиль/удаление."
    )
    await _reply(obj, text, _menu_kb())

async def show_privacy(obj: Message | CallbackQuery):
    text = (
        "🔐 Политика конфиденциальности\n\n"
        "Мы бережно храним ваши данные и используем их только для работы бота.\n"
        "Удаление профиля доступно в ⚙️ Настройках."
    )
    await _reply(obj, text, _back_kb())

async def show_settings(obj: Message | CallbackQuery):
    text = "⚙️ Настройки\n\nЗдесь можно удалить профиль или вернуться в меню."
    await _reply(obj, text, _settings_kb())

# ---------- хэндлеры раздела «Помощь» ----------

@router.message(Command("help"))
async def cmd_help(m: Message):
    await show_main_menu(m)

@router.message(Command("settings"))
async def cmd_settings(m: Message):
    await show_settings(m)

@router.message(Command("privacy"))
async def cmd_privacy(m: Message):
    await show_privacy(m)

# кнопки с reply-клавиатуры, если она включена
@router.message(F.text.in_({"💬 Помощь", "Помощь"}))
async def txt_help(m: Message):
    await show_main_menu(m)

@router.message(F.text.in_({"⚙️ Настройки", "Настройки"}))
async def txt_settings(m: Message):
    await show_settings(m)

@router.message(F.text.in_({"🔐 Политика", "Политика"}))
async def txt_privacy(m: Message):
    await show_privacy(m)

# те же переходы по инлайн-кнопкам
@router.callback_query(F.data == "go:menu")
async def cb_menu(cb: CallbackQuery):
    await show_main_menu(cb)

@router.callback_query(F.data == "go:privacy")
async def cb_privacy(cb: CallbackQuery):
    await show_privacy(cb)

@router.callback_query(F.data == "go:settings")
async def cb_settings(cb: CallbackQuery):
    await show_settings(cb)

__all__ = ["router", "show_main_menu", "show_privacy", "show_settings"]
