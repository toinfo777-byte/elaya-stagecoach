from __future__ import annotations

from datetime import date

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from app.core_client import send_timeline_event, fetch_progress
from .keyboards import MAIN_MENU, BTN_TRAINING_DAY

router = Router()


class TrainingFlow(StatesGroup):
    vector = State()      # 1. Вхождение в день
    reflect = State()     # 2. Отражение
    transition = State()  # 3. Маленький шаг
    review = State()      # 4. Финальное слово


# --- Старт тренировки -----------------------------------------------------


@router.message(F.text == BTN_TRAINING_DAY)
async def start_training(message: Message, state: FSMContext) -> None:
    """
    Старт тренировки дня.
    """
    # на всякий случай чистим старое состояние
    await state.clear()

    await send_timeline_event(
        scene="trainer.day.start",
        payload={"user_id": message.from_user.id},
    )

    await message.answer(
        "Старт тренировки дня.\n\n"
        "1️⃣ Коротко напиши — в каком состоянии ты входишь в день.\n"
        "Что сейчас главное в тебе / в поле?"
    )

    await state.set_state(TrainingFlow.vector)


# --- Вопрос 1 -------------------------------------------------------------


@router.message(TrainingFlow.vector)
async def handle_vector(message: Message, state: FSMContext) -> None:
    await state.update_data(vector=message.text.strip())

    await message.answer(
        "2️⃣ Теперь отражение.\n\n"
        "Посмотри на свой день / практику со стороны — "
        "что ты видишь о себе, о движении, о качестве присутствия?"
    )

    await state.set_state(TrainingFlow.reflect)


# --- Вопрос 2 -------------------------------------------------------------


@router.message(TrainingFlow.reflect)
async def handle_reflect(message: Message, state: FSMContext) -> None:
    await state.update_data(reflect=message.text.strip())

    await message.answer(
        "3️⃣ Маленький шаг.\n\n"
        "Какой один небольшой переход ты готов сделать после этой тренировки?\n"
        "Что можно изменить уже сегодня — на 1–2 шага?"
    )

    await state.set_state(TrainingFlow.transition)


# --- Вопрос 3 -------------------------------------------------------------


@router.message(TrainingFlow.transition)
async def handle_transition(message: Message, state: FSMContext) -> None:
    await state.update_data(transition=message.text.strip())

    await message.answer(
        "4️⃣ Финальное слово.\n\n"
        "Напиши пару фраз — как тебе эта тренировка, "
        "в каком состоянии ты выходишь."
    )

    await state.set_state(TrainingFlow.review)


# --- Вопрос 4 + завершение -----------------------------------------------


@router.message(TrainingFlow.review)
async def handle_review(message: Message, state: FSMContext) -> None:
    review = message.text.strip()
    data = await state.get_data()

    user_id = message.from_user.id

    # фиксируем тренировку в ядре
    await send_timeline_event(
        scene="trainer.day.finish",
        payload={
            "user_id": user_id,
            "date": date.today().isoformat(),
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
