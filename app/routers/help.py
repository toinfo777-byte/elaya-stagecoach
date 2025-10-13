from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

help_router = Router(name="help")

@help_router.message(Command("help", "faq"))
@help_router.message(F.text.casefold().in_({"💬 помощь / faq", "помощь", "faq"}))
async def show_help(m: Message):
    await m.answer(
        "💬 <b>Помощь / FAQ</b>\n\n"
        "• 🏋️ <b>Тренировка дня</b> — короткая ежедневная практика.\n"
        "• 📈 <b>Мой прогресс</b> — стрик и эпизоды за 7 дней.\n"
        "• 🧭 <b>Путь лидера</b> — в разработке, появится позже.\n\n"
        "Если что-то не работает — напиши /ping."
    )
