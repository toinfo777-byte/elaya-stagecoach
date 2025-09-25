# app/routers/entrypoints.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.reply import (
    main_menu_kb,
    BTN_TRAINING, BTN_PROGRESS, BTN_CASTING, BTN_APPLY,
    BTN_HELP, BTN_SETTINGS, BTN_EXTENDED, BTN_MENU,
)

router = Router(name="entrypoints")

@router.message(StateFilter("*"), F.text.in_({
    BTN_TRAINING, BTN_PROGRESS, BTN_CASTING, BTN_APPLY,
    BTN_HELP, BTN_SETTINGS, BTN_EXTENDED, BTN_MENU
}))
async def on_menu_button(m: Message, state: FSMContext):
    await state.clear()
    text = m.text or ""

    if text == BTN_CASTING:
        # 🎭 Мини-кастинг
        try:
            from app.routers.minicasting import start_minicasting
            return await start_minicasting(m, state)
        except Exception:
            pass

    elif text == BTN_APPLY:
        # 🧭 Путь лидера
        try:
            from app.routers.leader import start_leader_btn
            return await start_leader_btn(m, state)
        except Exception:
            pass

    elif text == BTN_PROGRESS:
        # 📈 Прогресс
        try:
            from app.routers.progress import show_progress
            return await show_progress(m)  # state не нужен
        except Exception:
            pass

    elif text == BTN_SETTINGS:
        # ⚙️ Настройки
        try:
            from app.routers.settings import open_settings
            return await open_settings(m, state)
        except Exception:
            pass

    elif text == BTN_HELP:
        # 💬 Помощь
        try:
            from app.routers.help import help_cmd
            return await help_cmd(m, state)
        except Exception:
            pass

    elif text == BTN_EXTENDED:
        # ⭐ Расширенная версия
        try:
            from app.routers.extended import extended_pitch
            return await extended_pitch(m)
        except Exception:
            pass

    # BTN_TRAINING или BTN_MENU, а также любые fallback’ы:
    await m.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
