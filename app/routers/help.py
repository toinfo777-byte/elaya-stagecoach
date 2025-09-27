# app/routers/help.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

router = Router(name="help")  # <-- main.py ждёт .router

# ---------- UI ----------
def _menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏋️ Тренировка дня", callback_data="go:training")],
        [InlineKeyboardButton(text="🎭 Мини-кастинг",     callback_data="go:casting")],
        [InlineKeyboardButton(text="🧭 Путь лидера",      callback_data="go:leader")],
        [InlineKeyboardButton(text="📈 Мой прогресс",     callback_data="go:progress")],
        [InlineKeyboardButton(text="🔐 Политика",         callback_data="go:privacy")],
        [InlineKeyboardButton(text="⚙️ Настройки",        callback_data="go:settings")],
    ])

def _back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")]
    ])

def _settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")]
    ])

# ---------- helpers ----------
async def _reply(obj: Message | CallbackQuery, text: str,
                 kb: InlineKeyboardMarkup | None = None):
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        return await obj.message.answer(text, reply_markup=kb)
    return await obj.answer(text, reply_markup=kb)

# ---------- публичные функции (их зовут другие роутеры) ----------
async def show_main_menu(obj: Message | CallbackQuery):
    text = (
        "Команды и разделы: выбери нужное ⤵️\n\n"
        "🏋️ Тренировка дня — ежедневная рутина 5–15 мин.\n"
        "🎭 Мини-кастинг — быстрый чек 2–3 мин.\n"
        "🧭 Путь лидера — цель + микро-задание + заявка.\n"
        "📈 Мой прогресс — стрик и эпизоды за 7 дней.\n"
        "🔐 Политика — как храним и используем ваши данные.\n"
        "⚙️ Настройки — профиль."
    )
    await _reply(obj, text, _menu_kb())

async def show_privacy(obj: Message | CallbackQuery):
    text = (
        "🔐 Политика: бережно храним данные и используем только для работы бота.\n"
        "Запрос на удаление — через «⚙️ Настройки»."
    )
    await _reply(obj, text, _back_kb())

async def show_settings(obj: Message | CallbackQuery):
    text = "⚙️ Настройки. Можешь вернуться в меню."
    await _reply(obj, text, _settings_kb())

# ---------- собственные хендлеры раздела «Помощь» ----------
@router.message(Command("help"))
async def cmd_help(m: Message):
    await show_main_menu(m)

# универсальные go:* из меню
@router.callback_query(F.data == "go:menu")
async def cb_menu(cb: CallbackQuery):
    await show_main_menu(cb)

@router.callback_query(F.data == "go:privacy")
async def cb_privacy(cb: CallbackQuery):
    await show_privacy(cb)

@router.callback_query(F.data == "go:settings")
async def cb_settings(cb: CallbackQuery):
    await show_settings(cb)

@router.callback_query(F.data == "go:training")
async def cb_training(cb: CallbackQuery):
    await cb.answer()
    from app.routers.training import show_training_levels
    await show_training_levels(cb.message)

@router.callback_query(F.data == "go:casting")
async def cb_casting(cb: CallbackQuery):
    await cb.answer()
    from app.routers.minicasting import start_minicasting
    await start_minicasting(cb)

@router.callback_query(F.data == "go:leader")
async def cb_leader(cb: CallbackQuery):
    await cb.answer()
    # импорт внутри — чтобы исключить циклы
    from app.routers.leader import leader_entry
    await leader_entry(cb)

@router.callback_query(F.data == "go:progress")
async def cb_progress(cb: CallbackQuery):
    await cb.answer()
    from app.routers.progress import show_progress
    await show_progress(cb)
