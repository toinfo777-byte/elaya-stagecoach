# app/routers/settings.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.keyboards.menu import BTN_SETTINGS, to_menu_inline, main_menu

router = Router(name="settings")


@router.message(F.text == BTN_SETTINGS)
@router.message(Command("settings"))
async def settings_open(m: Message):
    await m.answer(
        "Настройки. Можешь удалить профиль или вернуться в меню.",
        reply_markup=to_menu_inline()
    )


@router.callback_query(F.data == "settings:delete")
async def settings_delete(c: CallbackQuery, state: FSMContext):
    # TODO: добавить confirm-диалог и реальное удаление профиля из БД
    await state.clear()
    await c.message.answer(
        "Профиль удалён. Нажми /start, чтобы начать заново.",
        reply_markup=main_menu()
    )
    await c.answer()
