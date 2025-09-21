from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.keyboards.menu import main_menu

router = Router(name="casting")

# — ловим «мини-кастинг»/«кастинг» с любыми эмодзи/пробелами/регистром
CASTING_BTN_RE = r"(?is)^\s*(?:[\W_]*\s*)*(?:мини-)?кастинг"

# — deeplink вида: /start go_casting_post_2009 (и любые go_casting_*)
CASTING_START_RE = r"^/start(?:@\w+)?\s+go_casting_"

@router.message(Command("casting"))
@router.message(F.text.regexp(CASTING_BTN_RE))
async def casting_entry(m: Message) -> None:
    await m.answer("Мини-кастинг", reply_markup=main_menu())

@router.message(CommandStart(deep_link=True), F.text.regexp(CASTING_START_RE))
async def start_from_casting_deeplink(m: Message) -> None:
    await casting_entry(m)
