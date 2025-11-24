# trainer/app/routes/training_flow.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.core_api import send_timeline_event

router = Router(name="training")


# Вход в "Тренировку дня":
# 1) /training
# 2) нажатие кнопки "🏋️‍♂️ Тренировка дня"
@router.message(Command("training"))
@router.message(F.text.contains("Тренировка дня"))
async def training_entry(message: Message) -> None:
    # отправляем событие в ядро
    await send_timeline_event(
        scene="training_start",
        payload={
            "user_id": message.from_user.id if message.from_user else None,
            "username": message.from_user.username if message.from_user else None,
            "chat_id": message.chat.id,
            "text": message.text,
        },
    )

    await message.answer(
        "🟣 Тренировка дня скоро будет.\n"
        "Пока это тест связи с ядром — событие уже ушло в Таймлайн Элайи."
    )
