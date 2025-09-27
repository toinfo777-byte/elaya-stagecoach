# app/routers/cancel.py
from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import main_menu

router = Router(name="cancel")


@router.message(Command("cancel"))
async def cancel_cmd(m: Message) -> None:
    await m.answer("Ок, всё сбросил. Открываю меню.", reply_markup=main_menu())
