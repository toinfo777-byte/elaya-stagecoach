# app/routers/onboarding.py
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove

router = Router(name="onboarding")


def _is_private(msg: Message) -> bool:
    return msg.chat.type == "private"


# Если раньше у тебя здесь на on_startup/первом сообщении показывалось меню —
# убираем это поведение. Даём максимально «тихий» ответ, только в ЛС и без клавиатуры.
@router.message(F.text.regexp(r"^/start\s+.*"))
async def onboarding_payload(msg: Message):
    if not _is_private(msg):
        return
    await msg.answer(
        "Готов работать. Нажми /menu, чтобы открыть разделы.",
        reply_markup=ReplyKeyboardRemove(),
    )
