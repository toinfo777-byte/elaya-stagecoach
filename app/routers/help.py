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
        [InlineKeyboardButton(text="🏋️ Тренировка дня", callback_data="go:training")],  # ← добавили
        [InlineKeyboardButton(text="📈 Мой прогресс", callback_data="go:progress")],
        [InlineKeyboardButton(text="🔐 Политика", callback_data="go:privacy")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="go:settings")],
        [InlineKeyboardButton(text="⭐ Расширенная версия", callback_data="go:extended")],
    ])

HELP_HEADER = "Команды и разделы: выбери нужное ⤵️"

@router.message(StateFilter("*"), Command("help"))
@router.message(StateFilter("*"), F.text == BTN_HELP)
async def help_cmd(m: Message, state: FSMContext):
    await m.answer(HELP_HEADER, reply_markup=help_kb())

@router.callback_query(StateFilter("*"), F.data.startswith("go:"))
async def help_jump(cq: CallbackQuery, state: FSMContext):
    action = cq.data.split(":", 1)[1]
    await state.clear()

    if action == "menu":
        await cq.message.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())

    elif action == "casting":
        from app.routers.minicasting import start_minicasting_cmd
        await start_minicasting_cmd(cq.message, state)

    elif action == "apply":
        from app.routers.leader import start_leader_cmd
        await start_leader_cmd(cq.message, state)

    elif action == "training":
        from app.routers.training import training_start
        await training_start(cq.message, state)

    elif action == "progress":
        try:
            from app.routers.progress import show_progress
            await show_progress(cq.message)
        except Exception:
            await cq.message.answer("📈 Статистика недоступна. Открываю меню.", reply_markup=main_menu_kb())

    elif action == "privacy":
        from app.routers.privacy import PRIVACY_TEXT
        await cq.message.answer(PRIVACY_TEXT, reply_markup=main_menu_kb())

    elif action == "settings":
        await open_settings(cq.message, state)

    elif action == "extended":
        try:
            from app.routers.extended import extended_pitch
            await extended_pitch(cq.message)
        except Exception:
            await cq.message.answer("⭐ Расширенная версия скоро. Возвращаю в меню.", reply_markup=main_menu_kb())

    await cq.answer()
