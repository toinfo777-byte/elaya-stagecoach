from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.keyboards.menu import main_menu, BTN_CASTING

router = Router(name="casting")


# ── Общий запуск «Мини-кастинг»
@router.message(F.text == BTN_CASTING)
@router.message(Command("casting"))
async def casting_entry(m: Message) -> None:
    await m.answer("Мини-кастинг", reply_markup=main_menu())


# ── Deeplink только для кастинга
# ловим варианты:
#   /start go_casting_post_2009
#   /start@elaya_stagecoach_dev_bot go_casting_post_2009
CASTING_START_RE = r"^/start(?:@\w+)?\s+go_casting_"

@router.message(CommandStart(deep_link=True), F.text.regexp(CASTING_START_RE))
async def start_from_casting_deeplink(m: Message) -> None:
    # args = m.text.split(maxsplit=1)[1] if " " in m.text else ""
    await casting_entry(m)
