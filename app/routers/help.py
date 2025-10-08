from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

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

async def _reply(obj: Message | CallbackQuery, text: str,
                 kb: InlineKeyboardMarkup | None = None):
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        return await obj.message.answer(text, reply_markup=kb)
    return await obj.answer(text, reply_markup=kb)

async def show_main_menu(obj: Message | CallbackQuery):
    text = (
        "Команды и разделы: выбери нужное ⤵️\n\n"
        "🏋️ <b>Тренировка дня</b> — ежедневная рутина 5–15 мин.\n"
        "🎭 <b>Мини-кастинг</b> — быстрый чек 2–3 мин.\n"
        "🧭 <b>Путь лидера</b> — цель + микро-задание + заявка.\n"
        "📈 <b>Мой прогресс</b> — стрик и эпизоды за 7 дней.\n"
        "💬 <b>Помощь / FAQ</b> — ответы на частые вопросы.\n"
        "⚙️ <b>Настройки</b> — профиль.\n"
        "🔐 <b>Политика</b> — как храним и используем данные.\n"
        "⭐ <b>Расширенная версия</b> — скоро."
    )
    await _reply(obj, text, _menu_kb())

async def show_help(obj: Message | CallbackQuery):
    text = (
        "💬 <b>Помощь / FAQ</b>\n\n"
        "— Нажми «🏋️ Тренировка дня», чтобы начать.\n"
        "— «📈 Мой прогресс» покажет стрик и эпизоды.\n"
        "— «🧭 Путь лидера» — заявка и следующий шаг.\n\n"
        "Если что-то не работает — /ping."
    )
    await _reply(obj, text, _menu_kb())

async def show_privacy(obj: Message | CallbackQuery):
    await _reply(obj, "🔐 <b>Политика</b>\n\nДетали обновим перед релизом.", _menu_kb())

async def show_settings(obj: Message | CallbackQuery):
    await _reply(obj, "⚙️ <b>Настройки</b>\n\nПрофиль в разработке.", _menu_kb())

@help_router.message(CommandStart(deep_link=False))
async def start_no_payload(m: Message):
    await show_main_menu(m)

@help_router.message(Command("menu"))
async def cmd_menu(m: Message):
    await show_main_menu(m)

@help_router.message(Command("help"))
async def cmd_help(m: Message):
    await show_help(m)

@help_router.callback_query(lambda cq: cq.data == "go:help")
async def cb_help(cq: CallbackQuery):
    await show_help(cq)
