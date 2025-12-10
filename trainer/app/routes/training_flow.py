# trainer/app/routes/training_flow.py
from __future__ import annotations

from datetime import date

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU
from app.training_progress import register_training
from app.core_client import send_timeline_event

router = Router()


class TrainingFlow(StatesGroup):
    vector = State()
    reflect = State()
    transition = State()
    review = State()


# --- Вход в тренировку -------------------------------------------------------


async def start_training(message: Message, state: FSMContext) -> None:
    # Таймлайн: старт дня (ошибки логируются внутри send_timeline_event)
    await send_timeline_event(
        scene="trainer.day.start",
        payload={
            "tg_user_id": message.from_user.id,
        },
    )

    await state.set_state(TrainingFlow.vector)
    await message.answer(
        "Старт тренировки дня.\n\n"
        "1️⃣ Коротко напиши — в каком состоянии ты входишь в день.\n"
        "Что сейчас главное в тебе / в поле?"
    )


# --- Вопрос 1 ----------------------------------------------------------------


@router.message(TrainingFlow.vector)
async def handle_vector(message: Message, state: FSMContext) -> None:
    await state.update_data(vector=message.text.strip())

    await state.set_state(TrainingFlow.reflect)
    await message.answer(
        "2️⃣ Как ты видишь свой день со стороны?\n"
        "Каким он может быть, если ты будешь в присутствии?"
    )


# --- Вопрос 2 ----------------------------------------------------------------


@router.message(TrainingFlow.reflect)
async def handle_reflect(message: Message, state: FSMContext) -> None:
    await state.update_data(reflect=message.text.strip())

    await state.set_state(TrainingFlow.transition)
    await message.answer(
        "3️⃣ Какой один маленький шаг ты готов сделать сегодня,\n"
        "чтобы поддержать это состояние и этот день?"
    )


# --- Вопрос 3 ----------------------------------------------------------------


@router.message(TrainingFlow.transition)
async def handle_transition(message: Message, state: FSMContext) -> None:
    await state.update_data(transition=message.text.strip())

    await state.set_state(TrainingFlow.review)
    await message.answer(
        "📝 Если хочешь, напиши пару слов о том,\n"
        "как тебе сама настройка / тренировка.\n\n"
        "Можно просто отправить любой текст — даже один смайлик 🙂"
    )


# --- Завершение тренировки ---------------------------------------------------


@router.message(TrainingFlow.review)
async def handle_review(message: Message, state: FSMContext) -> None:
    review = message.text.strip()
    data = await state.get_data()

    # Сохраняем подробную тренировку (для будущей аналитики)
    register_training(
        user_id=message.from_user.id,
        date=date.today(),
        vector=data.get("vector", ""),
        reflect=data.get("reflect", ""),
        transition=data.get("transition", ""),
        review=review,
    )

    # Таймлайн: завершение дня
    await send_timeline_event(
        scene="trainer.day.finish",
        payload={
            "tg_user_id": message.from_user.id,
            "vector": data.get("vector", ""),
            "reflect": data.get("reflect", ""),
            "transition": data.get("transition", ""),
            "review": review,
        },
    )

    await state.clear()

    await message.answer(
        "Хорошая работа. Я сохранил твою тренировку.\n"
        "Если захочешь — нажимай «🎭 Тренировка дня».",
        reply_markup=MAIN_MENU,
    )
