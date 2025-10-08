from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

help_router = Router(name="help")

def _menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏋️ Тренировка дня",    callback_data="go:training")],
        [InlineKeyboardButton(text="🎭 Мини-кастинг",      callback_data="go:casting")],
        [InlineKeyboardButton(text="🧭 Путь лидера",       callback_data="go:leader")],
        [InlineKeyboardButton(text="📈 Мой прогресс",      callback_data="go:progress")],
        [InlineKeyboardButton(text="💬 Помощь / FAQ",      callback_data="go:help")],
        [InlineKeyboardButton(text="🔐 Политика",          callback_data="go:privacy")],
        [InlineKeyboardButton(text="⚙️ Настройки",         callback_data="go:settings")],
        [InlineKeyboardButton(text="⭐ Расширенная версия", callback_data="go:extended")],
    ])

async def _reply(obj: Message | CallbackQuery, text: str):
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        return await obj.message.answer(text, reply_markup=_menu_kb())
    return await obj.answer(text, reply_markup=_menu_kb())

async def show_help(obj: Message | CallbackQuery):
    text = (
        "💬 <b>Помощь / FAQ</b>\n\n"
        "— «🏋️ Тренировка дня» — старт здесь.\n"
        "— «📈 Мой прогресс» — стрик и эпизоды.\n"
        "— «🧭 Путь лидера» — заявка и шаги.\n\n"
        "Если что-то не работает — /ping."
    )
    await _reply(obj, text)

async def show_privacy(obj: Message | CallbackQuery):
    await _reply(obj, "🔐 <b>Политика</b>\n\nДетали обновим перед релизом.")

async def show_settings(obj: Message | CallbackQuery):
    await _reply(obj, "⚙️ <b>Настройки</b>\n\nПрофиль в разработке.")

@help_router.message(Command("help"))
async def cmd_help(m: Message): await show_help(m)

@help_router.callback_query(lambda cq: cq.data == "go:help")
async def cb_help(cq: CallbackQuery): await show_help(cq)
