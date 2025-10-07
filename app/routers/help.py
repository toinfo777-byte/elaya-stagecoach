from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

help_router = Router(name="help")

def _menu_kb() -> InlineKeyboardMarkup:
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

async def _reply(obj: Message | CallbackQuery, text: str,
                 kb: InlineKeyboardMarkup | None = None):
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        return await obj.message.answer(text, reply_markup=kb)
    return await obj.answer(text, reply_markup=kb)

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

# ── единые входы в меню ───────────────────────────────────────────

@help_router.message(CommandStart(deep_link=False))
async def start_no_payload(m: Message):
    await show_main_menu(m)

@help_router.message(Command("menu"))
async def cmd_menu(m: Message):
    await show_main_menu(m)

@help_router.callback_query(F.data == "go:menu"))
async def cb_go_menu(cb: CallbackQuery):
    await show_main_menu(cb)

# /help можно тоже сводить к главному меню
@help_router.message(Command("help"))
async def cmd_help(m: Message):
    await show_main_menu(m)

__all__ = ["help_router", "show_main_menu"]
