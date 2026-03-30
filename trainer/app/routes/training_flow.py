from __future__ import annotations

from datetime import date
import asyncio
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.keyboards.main_menu import (
    MAIN_MENU,
    BTN_TRAINING,
    BTN_PROGRESS,
    BTN_HELP,
    BTN_PREMIUM,
)
from app.training_progress import register_training
from app.core_client import send_timeline_event

router = Router()
logger = logging.getLogger(__name__)

ERROR_FALLBACK_TEXT = (
    "Похоже, что-то пошло не так на стороне сервера.\n"
    "Я уже отметил это в журнале.\n\n"
    "Попробуй ещё раз через пару минут или напиши в Штаб."
)


class TrainingFlow(StatesGroup):
    vector = State()
    reflect = State()
    transition = State()
    review = State()


@router.message(F.text == BTN_TRAINING)
async def handle_training_entry(message: Message, state: FSMContext) -> None:
    # ⚠️ НИЧЕГО НЕ ЖДЁМ
    asyncio.create_task(
        send_timeline_event(
            scene="trainer.day.start",
            payload={"tg_user_id": message.from_user.id},
        )
    )

    await state.set_state(TrainingFlow.vector)
    await message.answer(
        "Старт тренировки дня.\n\n"
        "1️⃣ Коротко напиши — в каком состоянии ты входишь в день."
    )


@router.message(TrainingFlow.vector)
async def handle_vector(message: Message, state: FSMContext) -> None:
    await state.update_data(vector=(message.text or "").strip())
    await state.set_state(TrainingFlow.reflect)
    await message.answer(
        "2️⃣ Как ты видишь свой день со стороны?"
    )


@router.message(TrainingFlow.reflect)
async def handle_reflect(message: Message, state: FSMContext) -> None:
    await state.update_data(reflect=(message.text or "").strip())
    await state.set_state(TrainingFlow.transition)
    await message.answer(
        "3️⃣ Какой маленький шаг ты готов сделать сегодня?"
    )


@router.message(TrainingFlow.transition)
async def handle_transition(message: Message, state: FSMContext) -> None:
    await state.update_data(transition=(message.text or "").strip())
    await state.set_state(TrainingFlow.review)
    await message.answer(
        "📝 Если хочешь — напиши пару слов о тренировке.\n"
        "Можно даже один смайлик 🙂"
    )


@router.message(TrainingFlow.review)
async def handle_review(message: Message, state: FSMContext) -> None:
    try:
        data = await state.get_data()
        review = (message.text or "").strip()

        register_training(
            user_id=message.from_user.id,
            date=date.today(),
            vector=data.get("vector", ""),
            reflect=data.get("reflect", ""),
            transition=data.get("transition", ""),
            review=review,
        )

        asyncio.create_task(
            send_timeline_event(
                scene="trainer.day.finish",
                payload={
                    "tg_user_id": message.from_user.id,
                    **data,
                    "review": review,
                },
            )
        )

        await state.clear()
        await message.answer(
            "Хорошая работа. Я сохранил твою тренировку.\n"
            "Если захочешь — нажимай «🎭 Тренировка дня».",
            reply_markup=MAIN_MENU,
        )

    except Exception as e:
        logger.exception("Trainer review error: %s", e)
        await state.clear()
        await message.answer(ERROR_FALLBACK_TEXT, reply_markup=MAIN_MENU)
