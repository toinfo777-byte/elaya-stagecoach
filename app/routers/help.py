# app/routers/help.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from app.keyboards.reply import main_menu_kb, BTN_HELP
from app.routers.settings import open_settings  # для перехода из help

router = Router(name="help")

def help_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Меню", callback_data="go:menu")],
        [InlineKeyboardButton(text="🎭 Мини-кастинг", callback_data="go:casting")],
        [InlineKeyboardButton(text="🧭 Путь лидера", callback_data="go:apply")],
        [InlineKeyboardButton(text="📈 Мой прогресс", callback_data="go:progress")],
        [InlineKeyboardButton(text="🔐 Политика", callback_data="go:privacy")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="go:settings")],
        [InlineKeyboardButton(text="⭐ Расширенная версия", callback_data="go:extended")],
    ])

HELP_HEADER = "Команды и разделы: выбери нужное ⤵️"

# Глобально: из любого состояния
@router.message(StateFilter("*"), Command("help"))
@router.message(StateFilter("*"), F.text == BTN_HELP)
async def help_cmd(m: Message, state: FSMContext):
    await m.answer(HELP_HEADER, reply_markup=help_kb())

@router.callback_query(F.data.startswith("go:"))
async def help_jump(cq: CallbackQuery, state: FSMContext):
    action = cq.data.split(":", 1)[1]
    # выходим из любых сценариев
    await state.clear()

    if action == "menu":
        await cq.message.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())

    elif action in {"casting", "apply"}:
        # Старт анкеты (кастинг/путь лидера) — делегируем в роутер casting
        try:
            from app.routers.casting import casting_entry  # локальный импорт, чтобы избежать циклов
            await casting_entry(cq.message, state)
        except Exception:
            await cq.message.answer("Открой меню и нажми «🎭 Мини-кастинг» или «🧭 Путь лидера».", reply_markup=main_menu_kb())

    elif action == "progress":
        await cq.message.answer(
            "📈 Мой прогресс\n\n• Стрик: 0\n• Этюдов за 7 дней: 0\n\n"
            "Продолжай каждый день — тренировка дня в один клик 👇",
            reply_markup=main_menu_kb()
        )

    elif action == "privacy":
        from app.routers.privacy import PRIVACY_TEXT
        await cq.message.answer(PRIVACY_TEXT, reply_markup=main_menu_kb())

    elif action == "settings":
        await open_settings(cq.message)  # наш хендлер настроек

    elif action == "extended":
        try:
            from app.routers.extended import extended_pitch
            await extended_pitch(cq.message)  # покажем пич
        except Exception:
            await cq.message.answer("⭐ Расширенная версия скоро. Возвращаю в меню.", reply_markup=main_menu_kb())

    await cq.answer()
