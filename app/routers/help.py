from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from app.keyboards.reply import main_menu_kb, BTN_HELP
from app.routers.settings import open_settings  # открываем настройки из help

router = Router(name="help")

HELP_HEADER = "Команды и разделы: выбери нужное ⤵️"


def help_kb() -> InlineKeyboardMarkup:
    # все пункты — ЧИСТЫЕ callback_data (никаких /команд)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Меню",              callback_data="go:menu")],
            [InlineKeyboardButton(text="🏋️ Тренировка дня",    callback_data="go:training")],
            [InlineKeyboardButton(text="🎭 Мини-кастинг",      callback_data="go:casting")],
            [InlineKeyboardButton(text="🧭 Путь лидера",       callback_data="go:apply")],
            [InlineKeyboardButton(text="📈 Мой прогресс",      callback_data="go:progress")],
            [InlineKeyboardButton(text="🔐 Политика",          callback_data="go:privacy")],
            [InlineKeyboardButton(text="⚙️ Настройки",         callback_data="go:settings")],
            [InlineKeyboardButton(text="⭐ Расширенная версия", callback_data="go:extended")],
        ]
    )


# Глобально: /help и кнопка «Помощь» работают из любого состояния
@router.message(StateFilter("*"), Command("help"))
@router.message(StateFilter("*"), F.text == BTN_HELP)
async def help_cmd(m: Message, state: FSMContext):
    await m.answer(HELP_HEADER, reply_markup=help_kb())


# Переходы по инлайн-кнопкам help
@router.callback_query(StateFilter("*"), F.data == "go:menu")
async def help_go_menu(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    await cq.message.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
    await cq.answer()


@router.callback_query(StateFilter("*"), F.data == "go:casting")
async def help_go_casting(cq: CallbackQuery, state: FSMContext):
    from app.routers.minicasting import start_minicasting  # локальный импорт, чтобы не ловить циклы
    await start_minicasting(cq.message, state)
    await cq.answer()


@router.callback_query(StateFilter("*"), F.data == "go:apply")
async def help_go_leader(cq: CallbackQuery, state: FSMContext):
    try:
        from app.routers.leader import start_leader
        await start_leader(cq.message, state)
    except Exception:
        await cq.message.answer("Открой меню и нажми «🧭 Путь лидера».", reply_markup=main_menu_kb())
    await cq.answer()


@router.callback_query(StateFilter("*"), F.data == "go:training")
async def help_go_training(cq: CallbackQuery, state: FSMContext):
    from app.routers.training import show_training_levels
    await show_training_levels(cq.message, state)
    await cq.answer()


@router.callback_query(StateFilter("*"), F.data == "go:progress")
async def help_go_progress(cq: CallbackQuery, state: FSMContext):
    # Лёгкий вариант без отдельного роутера «progress»
    # Если у тебя есть routers/progress.show_progress — можешь вызвать его вместо этого блока.
    try:
        from app.storage.repo_extras import get_progress
        streak, last7 = await get_progress(cq.from_user.id)
        text = (
            f"📈 Мой прогресс\n\n"
            f"• Стрик: {streak}\n"
            f"• Эпизодов за 7 дней: {last7}\n\n"
