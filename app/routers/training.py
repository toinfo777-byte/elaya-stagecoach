# app/routers/training.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.keyboards.menu import main_menu, BTN_TRAINING

router = Router(name="training")


@router.message(F.text == BTN_TRAINING)
@router.message(Command("training"))
async def training_entry(m: Message) -> None:
    await m.answer("Тренировка дня", reply_markup=main_menu())


TRAINING_START_RE = r"^/start(?:@\w+)?\s+go_training_"

@router.message(CommandStart(deep_link=True), F.text.regexp(TRAINING_START_RE))
async def start_from_training_deeplink(m: Message) -> None:
    await training_entry(m)
