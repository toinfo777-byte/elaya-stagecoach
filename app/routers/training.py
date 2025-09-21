from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.keyboards.menu import main_menu, BTN_TRAINING

router = Router(name="training")


# ── Общий запуск «Тренировка дня»
@router.message(F.text == BTN_TRAINING)
@router.message(Command("training"))
async def training_entry(m: Message) -> None:
    await m.answer("Тренировка дня", reply_markup=main_menu())


# ── Deeplink только для тренировки
# ловим варианты:
#   /start go_training_post_2009
#   /start@elaya_stagecoach_dev_bot go_training_post_2009
TRAINING_START_RE = r"^/start(?:@\w+)?\s+go_training_"

@router.message(CommandStart(deep_link=True), F.text.regexp(TRAINING_START_RE))
async def start_from_training_deeplink(m: Message) -> None:
    # если нужно, можно достать токен:
    # args = m.text.split(maxsplit=1)[1] if " " in m.text else ""
    await training_entry(m)
