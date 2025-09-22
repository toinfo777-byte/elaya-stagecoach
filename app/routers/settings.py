# app/routers/settings.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.reply import settings_kb, main_menu_kb, BTN_SETTINGS, BTN_MENU, BTN_DELETE
from app.storage.repo import delete_user  # async-функция удаления по tg_id

router = Router(name="settings")

SETTINGS_LOCK_KEY = "settings_shown"

# Глобально + антидубль
@router.message(StateFilter("*"), Command("settings"))
@router.message(StateFilter("*"), F.text == BTN_SETTINGS)
async def open_settings(m: Message, state: FSMContext):
    data = await state.get_data()
    if data.get(SETTINGS_LOCK_KEY):
        return
    await state.update_data(**{SETTINGS_LOCK_KEY: True})
    await m.answer("Настройки. Можешь удалить профиль или вернуться в меню.", reply_markup=settings_kb())

@router.message(StateFilter("*"), F.text == BTN_MENU)
async def back_to_menu(m: Message, state: FSMContext):
    await state.clear()  # чистим и флаг, и возможные сценарии
    await m.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())

@router.message(StateFilter("*"), F.text == BTN_DELETE)
async def delete_profile_handler(m: Message, state: FSMContext):
    await state.clear()
    try:
        await delete_user(m.from_user.id)
        text = "Готово. Профиль удалён."
    except Exception:
        text = "Не удалось удалить профиль. Попробуй позже."
    await m.answer(text, reply_markup=main_menu_kb())
