# trainer/app/routes/training.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from app.keyboards.main_menu import MAIN_MENU
from app.elaya_core import send_timeline_event


router = Router(name="training")


class TrainingFlow(StatesGroup):
    intro = State()
    reflect = State()
    transition = State()


# ───────────────────────────
# ВХОД В ТРЕНИРОВКУ
# ───────────────────────────

@router.message(Command("training"))
@router.message(F.text == "🏋️‍♂️ Тренировка дня")
async def start_training(message: Message, state: FSMContext) -> None:
    """
    Старт тренировочного цикла.
    Переводим пользователя в состояние intro и даём первый текст.
    Параллельно шлём событие в ядро.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id

    await state.set_state(TrainingFlow.intro)

    # событие в ядро — вход в тренировку
    await send_timeline_event(
        "intro",
        {
            "user_id": user_id,
            "chat_id": chat_id,
            "text": "",
        },
    )

    intro_text = (
        "Начинаем тренировку сцены.\n\n"
        "Шаг 1 — Вход.\n\n"
        "Опиши в нескольких фразах, как сейчас чувствует себя "
        "твоё тело, дыхание и голос."
    )

    await message.answer(intro_text, reply_markup=ReplyKeyboardRemove())


# ───────────────────────────
# ШАГ 1 — INTRO
# ───────────────────────────

@router.message(TrainingFlow.intro)
async def handle_intro(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_text = message.text or ""

    # фиксируем событие intro с текстом
    await send_timeline_event(
        "intro",
        {
            "user_id": user_id,
            "chat_id": chat_id,
            "text": user_text,
        },
    )

    reply_text = (
        "Спасибо.\n\n"
        "Шаг 2 — Отражение.\n"
        "Что ты заметил(а) в своём состоянии, пока писал(а) это? "
        "Одно-два наблюдения — без оценки."
    )

    await state.set_state(TrainingFlow.reflect)
    await message.answer(reply_text)


# ───────────────────────────
# ШАГ 2 — REFLECT
# ───────────────────────────

@router.message(TrainingFlow.reflect)
async def handle_reflect(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_text = message.text or ""

    # событие reflect
    await send_timeline_event(
        "reflect",
        {
            "user_id": user_id,
            "chat_id": chat_id,
            "text": user_text,
        },
    )

    reply_text = (
        "Отлично.\n\n"
        "Шаг 3 — Переход.\n"
        "Сделай один вывод: что из того, что ты сейчас заметил(а), "
        "ты хочешь забрать с собой на сегодня?"
    )

    await state.set_state(TrainingFlow.transition)
    await message.answer(reply_text)


# ───────────────────────────
# ШАГ 3 — TRANSITION / ЗАВЕРШЕНИЕ
# ───────────────────────────

@router.message(TrainingFlow.transition)
async def handle_transition(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_text = message.text or ""

    # событие transition
    await send_timeline_event(
        "transition",
        {
            "user_id": user_id,
            "chat_id": chat_id,
            "text": user_text,
        },
    )

    reply_text = (
        "Хорошо.\n\n"
        "На сегодня этого достаточно. "
        "Если захочешь продолжить — просто снова нажми «🏋️‍♂️ Тренировка дня»."
    )

    await state.clear()
    await message.answer(reply_text, reply_markup=MAIN_MENU)
