# app/routers/extended.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.texts.strings import EXTENDED_TEXT
from app.keyboards.menu import main_menu, BTN_EXTENDED

router = Router(name="extended")

@router.message(Command("extended"))
@router.message(F.text == BTN_EXTENDED)
async def ext_cmd(m: Message):
    await m.answer(EXTENDED_TEXT, reply_markup=main_menu())
