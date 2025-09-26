from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from app.keyboards.reply import main_menu_kb, BTN_HELP
from app.routers.settings import open_settings  # открыть настройки из help

router = Router(name="help")

HELP_HEADER = (
    "Команды и разделы: выбери нужное ⤵️\n\n"
    "🏋️ Тренировка дня — ежедневная рутина 5–15 мин.\n"
    "🎭 Мини-кастинг — быстрый чек 2–3 мин.\n"
    "🧭 Путь лидера — цель + микро-задание + заявка.\n"
    "📈 Мой прогресс — стрик и эпизоды за 7 дней.\n"
    "⚙️ Настройки — профиль.\n"
    "⭐ Расширенная версия — запрос доступа.\n"
)  # ← скобка закрыта

def help_kb() -> InlineKeyboardMarkup:
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

# ── /help и кнопка «Помощь» — из любого состояния
@router.message(StateFilter("*"), Command("help"))
@router.message(StateFilter("*"), F.text == BTN_HELP)
async def help_cmd(m: Message, state: FSMContext):
    await m.answer(HELP_HEADER, reply_markup=help_kb())

# ── переходы по кнопкам
@router.callback_query(StateFilter("*"), F.data == "go:menu")
async def help_go_menu(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    await cq.message.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
    await cq.answer()

@router.callback_query(StateFilter("*"), F.data == "go:casting")
async def help_go_casting(cq: CallbackQuery, state: FSMContext):
    from app.routers.minicasting import start_minicasting  # локальный импорт, чтобы избежать циклов
    await start_minicasting(cq.message, state)
    await cq.answer()

@router.callback_query(StateFilter("*"), F.data == "go:apply")
async def help_go_leader(cq: CallbackQuery, state: FSMContext):
    try:
        from app.routers.leader import start_leader_cmd  # есть почти во всех вариантах
        await start_leader_cmd(cq.message, state)
    except Exception:
        await cq.message.answer("Открой меню и нажми «🧭 Путь лидера».", reply_markup=main_menu_kb())
    await cq.answer()

@router.callback_query(StateFilter("*"), F.data == "go:training")
async def help_go_training(cq: CallbackQuery, state: FSMContext):
    from app.routers.training import show_training_levels  # публичный entry
    await show_training_levels(cq.message, state)
    await cq.answer()

@router.callback_query(StateFilter("*"), F.data == "go:progress")
async def help_go_progress(cq: CallbackQuery, state: FSMContext):
    try:
        from app.storage.repo_extras import get_progress
        streak, last7 = await get_progress(cq.from_user.id)
        text = (
            "📈 Мой прогресс\n\n"
            f"• Стрик: {streak}\n"
            f"• Эпизодов за 7 дней: {last7}\n\n"
            "Продолжай каждый день — «Тренировка дня» в один клик 👇"
        )
    except Exception:
        text = (
            "📈 Мой прогресс\n\n"
            "Статистика появится после первых тренировок.\n"
            "Начни с «🏋️ Тренировка дня» 👇"
        )
    await cq.message.answer(text, reply_markup=main_menu_kb())
    await cq.answer()

@router.callback_query(StateFilter("*"), F.data == "go:privacy")
async def help_go_privacy(cq: CallbackQuery, state: FSMContext):
    try:
        from app.routers.privacy import PRIVACY_TEXT
        await cq.message.answer(PRIVACY_TEXT, reply_markup=main_menu_kb())
    except Exception:
        await cq.message.answer("Политика скоро будет доступна. Возвращаю в меню.", reply_markup=main_menu_kb())
    await cq.answer()

@router.callback_query(StateFilter("*"), F.data == "go:settings")
async def help_go_settings(cq: CallbackQuery, state: FSMContext):
    await open_settings(cq.message, state)
    await cq.answer()

@router.callback_query(StateFilter("*"), F.data == "go:extended")
async def help_go_extended(cq: CallbackQuery, state: FSMContext):
    try:
        from app.routers.extended import extended_pitch
        await extended_pitch(cq.message)
    except Exception:
        await cq.message.answer("⭐ Расширенная версия скоро. Возвращаю в меню.", reply_markup=main_menu_kb())
    await cq.answer()
