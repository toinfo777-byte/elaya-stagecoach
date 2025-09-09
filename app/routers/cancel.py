# app/routers/cancel.py
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.menu import main_menu

router = Router(name="cancel")

@router.message(StateFilter("*"), Command("cancel"))
async def cancel_any(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Ок, всё сбросил. Открываю меню.", reply_markup=main_menu())
