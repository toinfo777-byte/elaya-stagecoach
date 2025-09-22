# app/routers/settings.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.reply import settings_kb, main_menu_kb, BTN_SETTINGS
from app.storage.repo import delete_user  # должна быть async-функция удаления по tg_id

router = Router(name="settings")


@router.message(Command("settings"))
@router.message(F.text == BTN_SETTINGS, StateFilter(None))
async def open_settings(m: Message):
    """Открываем экран настроек, только когда не в форме (StateFilter(None))."""
    await m.answer(
        "Настройки. Можешь удалить профиль или вернуться в меню.",
        reply_markup=settings_kb(),
    )


@router.message(F.text == "🏠 В меню")
async def back_to_menu(m: Message, state: FSMContext):
    """Всегда выходим в меню и сбрасываем состояние формы."""
    await state.clear()
    await m.answer("Меню", reply_markup=main_menu_kb())


@router.message(F.text == "🗑 Удалить профиль")
async def delete_profile_handler(m: Message, state: FSMContext):
    """Удаляем профиль (если есть), чистим состояние и возвращаемся в меню."""
    await state.clear()
    try:
        await delete_user(m.from_user.id)
        text = "Готово. Профиль удалён."
    except Exception:
        # Мягко обрабатываем непредвиденные проблемы, чтобы не «залипать»
        text = "Не удалось удалить профиль. Попробуй позже."
    await m.answer(text, reply_markup=main_menu_kb())
