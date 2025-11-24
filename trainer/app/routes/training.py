from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from app.core_api import send_timeline_event
from app.keyboards.main_menu import MAIN_MENU

router = Router(name="training")


class TrainingFlow(StatesGroup):
    intro = State()
    reflect = State()
    finish = State()


@router.message(Command("training"))
@router.message(F.text.lower().contains("трениров"))
async def start_training(message: Message, state: FSMContext) -> None:
    await state.clear()

    # 📌 Минимальное событие в таймлайн
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
        "Стартуем тренировку дня (минимальная версия).",
        reply_markup=ReplyKeyboardRemove(),
    )
    # дальше можно будет нарастить логику флоу
