# app/routers/reply_shortcuts.py
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.menu import BTN_MENU, BTN_SETTINGS, main_menu, settings_menu

router = Router(name="reply_shortcuts")


@router.message(F.text == BTN_MENU)
async def go_menu(message: Message, state: FSMContext):
    """Сброс FSM и возврат в меню из любого шага"""
    await state.clear()
    await message.answer("Меню", reply_markup=main_menu())


@router.message(F.text == BTN_SETTINGS)
async def go_settings(message: Message, state: FSMContext):
    """Сброс FSM и открытие настроек из любого шага"""
    await state.clear()
    await message.answer(
        "Настройки. Можешь удалить профиль или вернуться в меню.",
        reply_markup=settings_menu()
    )
