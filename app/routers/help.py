from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

from app.keyboards.reply import main_menu_kb  # ← reply-клавиатура «большое меню»

router = Router(name="help")

# ---------- UI (инлайн) ----------
def _help_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏋️ Тренировка дня", callback_data="go:training")],
        [InlineKeyboardButton(text="🎭 Мини-кастинг",   callback_data="go:casting")],
        [InlineKeyboardButton(text="🧭 Путь лидера",    callback_data="go:leader")],
        [InlineKeyboardButton(text="📈 Мой прогресс",   callback_data="go:progress")],
        [InlineKeyboardButton(text="🔐 Политика",       callback_data="go:privacy")],
        [InlineKeyboardButton(text="⚙️ Настройки",      callback_data="go:settings")],
        [InlineKeyboardButton(text="🏠 В меню",         callback_data="go:menu")],
    ])

def _back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
        [InlineKeyboardButton(text="💬 Помощь", callback_data="go:help")],
    ])

# ---------- утилита для ответа в Message | CallbackQuery ----------
async def _reply(obj: Message | CallbackQuery, text: str,
                 kb: InlineKeyboardMarkup | None = None):
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        return await obj.message.answer(text, reply_markup=kb)
    return await obj.answer(text, reply_markup=kb)

# ---------- ПУБЛИЧНЫЕ ЭКРАНЫ (используются в entrypoints) ----------

async def show_main_menu(obj: Message | CallbackQuery):
    """Главное меню: короткое «Готово!» + reply-клавиатура."""
    await _reply(obj, "Готово! Открываю меню.", kb=None)
    # отправляем отдельным сообщением reply-клавиатуру
    msg = obj.message if isinstance(obj, CallbackQuery) else obj
    await msg.answer("Выбери раздел ⤵️", reply_markup=main_menu_kb())

async def show_help(obj: Message | CallbackQuery):
    """Помощь: описание разделов + инлайн-кнопки go:*."""
    text = (
        "Команды и разделы: выбери нужное ⤵️\n\n"
        "🏋️ Тренировка дня — ежедневная рутина 5–15 мин.\n"
        "🎭 Мини-кастинг — быстрый чек 2–3 мин.\n"
        "🧭 Путь лидера — цель + микро-задание + заявка.\n"
        "📈 Мой прогресс — стрик и эпизоды за 7 дней.\n"
        "🔐 Политика — как храним и используем ваши данные.\n"
        "⚙️ Настройки — профиль/удаление."
    )
    await _reply(obj, text, _help_kb())

async def show_privacy(obj: Message | CallbackQuery):
    text = (
        "🔐 Политика конфиденциальности\n\n"
        "Мы бережно храним ваши данные и используем их только для работы бота.\n"
        "Удаление профиля — в ⚙️ Настройках."
    )
    await _reply(obj, text, _back_kb())

async def show_settings(obj: Message | CallbackQuery):
    text = "⚙️ Настройки\n\nЗдесь можно удалить профиль или вернуться в меню."
    await _reply(obj, text, _back_kb())

# ---------- ХЭНДЛЕРЫ РАЗДЕЛА «Помощь» ----------

@router.message(Command("help"))
async def cmd_help(m: Message):
    await show_help(m)

@router.message(F.text.in_({"💬 Помощь", "Помощь"}))
async def txt_help(m: Message):
    await show_help(m)

@router.callback_query(F.data == "go:help")
async def cb_help(cb: CallbackQuery):
    await show_help(cb)

@router.callback_query(F.data == "go:menu")
async def cb_menu(cb: CallbackQuery):
    await show_main_menu(cb)

@router.callback_query(F.data == "go:privacy")
async def cb_privacy(cb: CallbackQuery):
    await show_privacy(cb)

@router.callback_query(F.data == "go:settings")
async def cb_settings(cb: CallbackQuery):
    await show_settings(cb)

__all__ = ["router", "show_main_menu", "show_help", "show_privacy", "show_settings"]
