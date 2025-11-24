from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU
from app.core_api import send_timeline_event

router = Router(name="menu")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_id = message.from_user.id
    chat_id = message.chat.id

    await send_timeline_event(
        scene="start",
        payload={
            "user_id": user_id,
            "chat_id": chat_id,
            "text": "/start",
        },
    )

    await message.answer(
        "Привет. Я — тренер Элайи.\n\n"
        "Выбери режим:",
        reply_markup=MAIN_MENU,
    )
