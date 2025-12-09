# trainer/app/routers/onboarding.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove

router = Router(name="onboarding")


def _is_private(msg: Message) -> bool:
    return msg.chat.type == "private"


# Тихий /start: только в ЛС, без клавиатуры и без автопоказа меню
@router.message(F.text.regexp(r"^/start\b"))
async def onboarding_payload(msg: Message) -> None:
    if not _is_private(msg):
        return

    await msg.answer(
        "Готов работать. Нажми /menu, чтобы открыть разделы.",
        reply_markup=ReplyKeyboardRemove(),
    )
