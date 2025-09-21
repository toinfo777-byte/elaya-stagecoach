from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.keyboards.menu import main_menu

router = Router(name="training")

# — текст кнопки ловим по "трениров" без учёта регистра и любых эмодзи/пробелов
TRAINING_BTN_RE = r"(?is)^\s*(?:[\W_]*\s*)*трениров"

# — deeplink вида: /start go_training_post_2009 (и любые go_training_*)
TRAINING_START_RE = r"^/start(?:@\w+)?\s+go_training_"

@router.message(Command("training"))
@router.message(F.text.regexp(TRAINING_BTN_RE))
async def training_entry(m: Message) -> None:
    await m.answer("Тренировка дня", reply_markup=main_menu())

@router.message(CommandStart(deep_link=True), F.text.regexp(TRAINING_START_RE))
async def start_from_training_deeplink(m: Message) -> None:
    await training_entry(m)
