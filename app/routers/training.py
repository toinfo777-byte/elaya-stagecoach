from __future__ import annotations

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from app.core_api import send_timeline_event
from app.keyboards.main_menu import MAIN_MENU

router = Router(name="training-router")


class TrainingFlow(StatesGroup):
    intro = State()
    reflect = State()
    transition = State()


# 🚀 вход в тренировку дня
@router.message(F.text == "🏋️‍♂️ Тренировка дня")
@router.message(F.text == "🏋️ Тренировка дня")
async def start_training(message: Message, state: FSMContext) -> None:
    await state.clear()

    await send_timeline_event(
        "training:intro:start",
        {"user_id": message.from_user.id, "username": message.from_user.username},
    )

    await message.answer(
        (
            "Начинаем <b>Тренировку дня</b>.\n\n"
            "1️⃣ <b>Вход в тело</b>\n"
            "Сделай пару спокойных вдохов и выдохов.\n"
            "Опиши в 1–3 предложениях, что сейчас ощущает твой голос и дыхание."
        ),
        reply_markup=ReplyKeyboardRemove(),
    )

    await state.set_state(TrainingFlow.intro)


# 🟡 блок intro
@router.message(TrainingFlow.intro)
async def handle_intro(message: Message, state: FSMContext) -> None:
    await state.update_data(intro_text=message.text)

    await send_timeline_event(
        "training:intro:text",
        {
            "user_id": message.from_user.id,
            "text": message.text,
        },
    )

    await message.answer(
        (
            "2️⃣ <b>Отражение</b>\n"
            "Посмотри на своё состояние со стороны.\n"
            "Что в нём кажется тебе сильным, а что — хрупким?\n"
            "Напиши 2–3 короткие мысли."
        )
    )

    await state.set_state(TrainingFlow.reflect)


# 🔵 блок reflect
@router.message(TrainingFlow.reflect)
async def handle_reflect(message: Message, state: FSMContext) -> None:
    await state.update_data(reflect_text=message.text)

    await send_timeline_event(
        "training:reflect:text",
        {
            "user_id": message.from_user.id,
            "text": message.text,
        },
    )

    await message.answer(
        (
            "3️⃣ <b>Переход</b>\n"
            "Сделай один маленький сдвиг.\n"
            "Какое <b>одно действие</b> ты сегодня сделаешь иначе, "
            "чтобы голос стал свободнее и увереннее?\n"
            "Опиши это в одном предложении."
        )
    )

    await state.set_state(TrainingFlow.transition)


# 🟣 блок transition + завершение
@router.message(TrainingFlow.transition)
async def handle_transition(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()

    await send_timeline_event(
        "training:transition:done",
        {
            "user_id": message.from_user.id,
            "transition_text": message.text,
            "intro_text": data.get("intro_text", ""),
            "reflect_text": data.get("reflect_text", ""),
        },
    )

    await message.answer(
        (
            "🔥 <b>Тренировка дня завершена</b>.\n\n"
            "Ты зафиксировал состояние, посмотрел на него со стороны и выбрал шаг.\n"
            "Когда почувствуешь, что цикл прожит — можно вернуться к меню."
        ),
        reply_markup=MAIN_MENU,
    )
