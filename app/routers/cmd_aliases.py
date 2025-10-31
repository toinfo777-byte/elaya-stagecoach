from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.enums import ChatType

router = Router(name="cmd_aliases")

@router.message(Command("start", "menu"), F.chat.type == ChatType.PRIVATE)
async def aliases_private(m: Message) -> None:
    await m.bot.dispatcher.feed_update(m.update)  # передаём дальше; старт/меню уже перехватят entrypoints.py

@router.message(Command("start", "menu"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def aliases_group(m: Message) -> None:
    await m.answer("Откройте меня в ЛС, там есть меню.", reply_markup=ReplyKeyboardRemove(True))
