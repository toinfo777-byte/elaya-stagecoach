from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.enums import ChatType

router = Router(name="help")

@router.message(Command("help"), F.chat.type == ChatType.PRIVATE)
async def help_private(m: Message) -> None:
    await m.answer("FAQ и помощь. Задавайте вопрос.")

@router.message(Command("help"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def help_group(m: Message) -> None:
    await m.answer("Помощь доступна в личке. Напишите мне в ЛС.", reply_markup=ReplyKeyboardRemove(True))
