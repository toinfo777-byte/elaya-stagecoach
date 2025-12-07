from __future__ import annotations

from datetime import date
from typing import Any, Dict

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from app.core_client import send_timeline_event
from .menu import MAIN_MENU

router = Router()


# --- FSM состояния ------------------------------------------------------------

class TrainingFlow(StatesGroup):
    intro = State()      # 1. Вход в день
    reflect = State()    # 2. Отражение
    step = State()       # 3. Маленький шаг
    review = State()     # 4. Финальное слово


# --- Старт тренировки ---------------------------------------------------------


@router.message(F.text == "🎭 Тренировка дня")
async def start_training(message: Message, state: FSMContext) -> None:
    """
    Точка входа в дневную тренировку.
    """
    # Сбрасываем возможные старые состояния
    await state.clear()

    # Телеметрия в ядро (если настроено)
    await send_timeline_event(
        "trainer.day.start",
        payload={
            "user_id": message.from_user.id if message.from_user else None,
            "date": date.today().isoformat(),
        },
    )

    await state.set_state(TrainingFlow.intro)

    await message.answer(
        "Старт тренировки дня.\n\n"
        "1️⃣ Коротко напиши — в каком состоянии ты входишь в день.\n"
        "Что сейчас главное в тебе / в поле?",
    )


# --- 1. Вход в день -----------------------------------------------------------


@router.message(TrainingFlow.intro)
async def handle_intro(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    await state.update_data(vector=text)

    await state.set_state(TrainingFlow.reflect)
    await message.answer(
        "2️⃣ Теперь отражение.\n\n"
        "Посмотри на свой день / практику со стороны — "
        "что ты видишь о себе, о движении, о качестве присутствия?",
    )


# --- 2. Отражение -------------------------------------------------------------


@router.message(TrainingFlow.reflect)
async def handle_reflect(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    await state.update_data(reflect=text)

    await state.set_state(TrainingFlow.step)
    await message.answer(
        "3️⃣ Маленький шаг.\n\n"
        "Какой один небольшой переход ты готов сделать после этой тренировки?\n"
        "Что можно изменить уже сегодня — на 1–2 шага?",
    )


# --- 3. Маленький шаг ---------------------------------------------------------


@router.message(TrainingFlow.step)
async def handle_step(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    await state.update_data(transition=text)

    await state.set_state(TrainingFlow.review)
    await message.answer(
        "4️⃣ Финальное слово.\n\n"
        "Напиши пару фраз — как тебе эта тренировка, "
        "в каком состоянии ты выходишь.",
    )


# --- 4. Финальное слово + завершение -----------------------------------------


@router.message(TrainingFlow.review)
async def handle_review(message: Message, state: FSMContext) -> None:
    review = (message.text or "").strip()
    data: Dict[str, Any] = await state.get_data()

    user_id = message.from_user.id if message.from_user else 0

    # Отправляем всё ядру (оно уже само решит, как сохранять)
    await send_timeline_event(
        "trainer.day.finish",
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
