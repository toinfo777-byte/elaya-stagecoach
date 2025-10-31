# app/routers/cmd_aliases.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram.types import Message, ReplyKeyboardRemove

router = Router(name="cmd_aliases")

@router.message(Command("start", "menu"), F.chat.type == ChatType.PRIVATE)
async def aliases_private(m: Message) -> None:
    # прокидываем дальше, если у тебя есть центральный обработчик
    await m.bot.dispatcher.feed_update(m.update)

@router.message(Command("start", "menu"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def aliases_group(m: Message) -> None:
    await m.answer(
        "Откройте меня в личке — там есть меню.",
        reply_markup=ReplyKeyboardRemove(),
    )
