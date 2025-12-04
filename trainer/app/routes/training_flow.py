# trainer/app/routes/training_flow.py
from __future__ import annotations

from datetime import date

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from ..menu import MAIN_MENU
from ..core_client import send_timeline_event


router = Router(name="training_flow")

# пока один пользователь — этого достаточно
USER_ID = 1


class TrainingFlow(StatesGroup):
    """
    FSM-тренировки дня:
    1) vector      — состояние / вектор входа
    2) reflect     — рефлексия по дню / тренировке
    3) transition  — маленький переход / шаг
    4) review      — финальное слово / отзыв
    """
    vector = State()
    reflect = State()
    transition = State()
    review = State()


# --- Старт тренировки -------------------------------------------------


@router.message(F.text == "🎭 Тренировка дня")
async def start_training(message: Message, state: FSMContext) -> None:
    """
    Запуск тренировки дня:
    - ставим состояние на ввод "vector"
    - шлём событие trainer.day.start в ядро
    """
    await state.clear()
    await state.set_state(TrainingFlow.vector)

    # 🟣 Событие «тренировка стартовала»
    await send_timeline_event(
        scene="trainer.day.start",
        payload={
            "user_id": USER_ID,
            "date": date.today().isoformat(),
            "chat_id": message.chat.id,
        },
    )

    await message.answer(
        "Старт тренировки дня.\n\n"
        "1️⃣ Коротко напиши — в каком состоянии ты входишь в день.\n"
        "Что сейчас главное в тебе / в поле?",
        reply_markup=MAIN_MENU,
    )


# --- Шаг 1: vector ----------------------------------------------------


@router.message(TrainingFlow.vector)
async def handle_vector(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    await state.update_data(vector=text)

    await state.set_state(TrainingFlow.reflect)
    await message.answer(
        "2️⃣ Теперь отражение.\n\n"
        "Посмотри на свой день / практику со стороны — "
        "что ты видишь о себе, о движении, о качестве присутствия?",
        reply_markup=MAIN_MENU,
    )


# --- Шаг 2: reflect ---------------------------------------------------


@router.message(TrainingFlow.reflect)
async def handle_reflect(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    await state.update_data(reflect=text)

    await state.set_state(TrainingFlow.transition)
    await message.answer(
        "3️⃣ Маленький шаг.\n\n"
        "Какой один небольшой переход ты готов сделать после этой тренировки?\n"
        "Что можно изменить уже сегодня — на 1–2 шага?",
        reply_markup=MAIN_MENU,
    )


# --- Шаг 3: transition ------------------------------------------------


@router.message(TrainingFlow.transition)
async def handle_transition(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    await state.update_data(transition=text)

    await state.set_state(TrainingFlow.review)
    await message.answer(
        "4️⃣ Финальное слово.\n\n"
        "Напиши пару фраз — как тебе эта тренировка, "
        "в каком состоянии ты выходишь.",
        reply_markup=MAIN_MENU,
    )


# --- Шаг 4: review + сохранение --------------------------------------


@router.message(TrainingFlow.review)
async def handle_review(message: Message, state: FSMContext) -> None:
    review = (message.text or "").strip()
    data = await state.get_data()

    # 👉 отправляем событие в ядро (Stagecoach Web)
    await send_timeline_event(
        scene="trainer.day.finish",
        payload={
            "user_id": message.from_user.id,
            "date": date.today().isoformat(),
            "vector": data.get("vector", ""),
            "reflect": data.get("reflect", ""),
            "transition": data.get("transition", ""),
            "review": review,
        },
    )

    await state.clear()

    # ⭐ Финальное сообщение + возвращаем меню
    await message.answer(
        "Хорошая работа. Я сохранил твою тренировку.\n"
        "Если захочешь — нажимай «🎭 Тренировка дня».",
        reply_markup=MAIN_MENU,
    )
