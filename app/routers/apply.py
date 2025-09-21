# app/routers/apply.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import main_menu, BTN_LEADER

router = Router(name="apply")


@router.message(F.text == BTN_LEADER)
@router.message(Command("apply"))
async def apply_entry(m: Message) -> None:
    await m.answer("Путь лидера — заявка. (Здесь будет форма/инструкция)", reply_markup=main_menu())
