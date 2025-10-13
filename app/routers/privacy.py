from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

privacy_router = Router(name="privacy")

@privacy_router.message(Command("policy"))
@privacy_router.message(F.text.casefold().in_({"🔐 политика", "политика", "policy"}))
async def show_policy(m: Message):
    await m.answer(
        "🔐 <b>Политика</b>\n\n"
        "Мы бережно относимся к данным. Личные сведения не собираем.\n"
        "Диалоги используются только для обучения навыкам речи.\n"
        "Можно в любой момент завершить работу командой /stop."
    )
