# trainer/app/routes/training_flow.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU
from app.core_api import send_timeline_event

router = Router(name="training_flow")


# --- FSM ---

class TrainingFlow(StatesGroup):
    intro = State()
    reflect = State()
    transition = State()


# --- вход в тренировку ---

@router.message(Command("training"))
@router.message(F.text == "🏋️‍♂️ Тренировка дня")
async def training_start(message: Message, state: FSMContext):
    """
    Первый вход в тренировку.
    """
    await state.set_state(TrainingFlow.intro)

    # отправляем событие в CORE
    await send_timeline_event(
        source="trainer-bot",
        scene="training_start",
        payload={"user": message.from_user.id},
    )

    await message.answer(
        "Начинаем тренировку дня.\n"
        "Сделай мягкий вдох, почувствуй центр груди.\n"
        "Готов продолжать?",
        reply_markup=MAIN_MENU,
    )


# --- шаг 2 ---

@router.message(TrainingFlow.intro)
async def training_reflect(message: Message, state: FSMContext):
    await state.set_state(TrainingFlow.reflect)

    await send_timeline_event(
        source="trainer-bot",
        scene="training_intro_done",
        payload={"text": message.text},
    )

    await message.answer(
        "Отлично. Теперь скажи одним словом — какое у тебя состояние?",
        reply_markup=MAIN_MENU,
    )


# --- шаг 3 ---

@router.message(TrainingFlow.reflect)
async def training_transition(message: Message, state: FSMContext):
    await state.set_state(TrainingFlow.transition)

    await send_timeline_event(
        source="trainer-bot",
        scene="training_reflect_done",
        payload={"state": message.text},
    )

    await message.answer(
        "Хорошо. Последний шаг.\n"
        "Сделай выдох. Почувствуй опору.\n"
        "Готово.",
        reply_markup=MAIN_MENU,
    )

    # завершаем FSM
    await state.clear()

