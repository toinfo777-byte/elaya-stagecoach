# app/routers/deeplink.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.routers.training import training_entry   # функция, которая открывает уровни
from app.routers.casting import start_casting_flow  # функция анкеты
from app.keyboards.menu import main_menu

router = Router(name="deeplink")


@router.message(CommandStart())
async def start_with_deeplink(message: Message, command: CommandObject, state: FSMContext):
    # всегда чистим состояние
    await state.clear()
    payload = (command.args or "").strip() if command else ""

    if payload.startswith("go_training"):
        return await training_entry(message)

    if payload.startswith("go_casting"):
        return await start_casting_flow(message, state)

    # если ничего не подошло → дефолт
    await message.answer("Готово! Открываю меню.", reply_markup=main_menu())
