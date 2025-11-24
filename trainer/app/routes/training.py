from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message

from app.elaya_core import send_timeline_event
from app.keyboards.main_menu import MAIN_MENU

router = Router(name="training")

@router.message(F.text.lower().contains("тренировка дня"))
async def training_entry(msg: Message):
    await msg.answer("Запускаю тренировку…", reply_markup=MAIN_MENU)
    await send_timeline_event("training_day", {"user_id": msg.from_user.id})
