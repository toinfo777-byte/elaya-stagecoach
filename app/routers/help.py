# app/routers/help.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.texts.strings import HELP_TEXT
from app.keyboards.menu import main_menu, BTN_HELP

router = Router(name="help")

@router.message(Command("help"))
@router.message(F.text == BTN_HELP)
async def help_cmd(m: Message):
    await m.answer(HELP_TEXT, reply_markup=main_menu())
