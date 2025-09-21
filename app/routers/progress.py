from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import main_menu, BTN_PROGRESS if 'BTN_PROGRESS' in dir(__import__('app.keyboards.menu', fromlist=['*'])) else None
from app.storage.mvp_repo import progress_for

# На случай если у вас константа называется иначе:
try:
    from app.keyboards.menu import BTN_PROGRESS  # noqa
except Exception:
    BTN_PROGRESS = "📈 Мой прогресс"

router = Router(name="progress")


@router.message(F.text == BTN_PROGRESS)
@router.message(Command("progress"))
async def show_progress(m: Message) -> None:
    streak, last7 = progress_for(m.from_user.id)
    await m.answer(
        "<b>Мой прогресс</b>\n"
        f"• Стрик: {streak}\n"
        f"• Эпизодов за 7 дней: {last7}\n\n"
        "Продолжай каждый день — «Тренировка дня» в один клик 👇",
        reply_markup=main_menu()
    )
