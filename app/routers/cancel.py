from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.menu import main_menu

router = Router(name="cancel")


@router.message(Command("cancel"))
async def cancel_any_state(m: Message, state: FSMContext) -> None:
    await state.clear()
    await m.answer("Ок, всё сбросил. Открываю меню.", reply_markup=main_menu())
