# trainer/app/routes/training.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from app.core_api import scene_enter, scene_reflect, scene_transition
from app.keyboards.main_menu import MAIN_MENU
from app.elaya_core import send_timeline_event

router = Router(name="training")


class TrainingFlow(StatesGroup):
    intro = State()
    reflect = State()
    transition = State()


# Вход в тренировку:
# 1) команда /training
# 2) любая кнопка / текст, где есть "Тренировка дня"
@router.message(Command("training"))
@router.message(F.text.contains("Тренировка дня"))
async def start_training(message: Message, state: FSMContext):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # 1) обращаемся к CORE за текстом сцены "intro"
    try:
        reply_text = await scene_enter(
            user_id=user_id,
            chat_id=chat_id,
            scene="intro",
        )
    except Exception:
        # запасной текст, если CORE недоступен
        reply_text = (
            "Начнём тренировку.\n\n"
            "Напиши в двух-трёх предложениях, что ты хочешь прокачать сегодня."
        )

    # 2) отправляем событие в таймлайн
    await send_timeline_event(
        scene="intro",
        payload={
            "user_id": user_id,
            "chat_id": chat_id,
            "text": message.text or "",
        },
    )

    # 3) ставим состояние и спрашиваем пользователя
    await state.set_state(TrainingFlow.intro)
    await message.answer(
        reply_text,
        reply_markup=ReplyKeyboardRemove(),
    )


# Шаг 2 — пользователь отвечает в "intro"
@router.message(TrainingFlow.intro)
async def handle_intro(message: Message, state: FSMContext):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_text = message.text or ""

    try:
        reply_text = await scene_reflect(
            user_id=user_id,
            chat_id=chat_id,
            scene="reflect",
            text=user_text,
        )
    except Exception:
        reply_text = (
            "Принял.\n\n"
            "Теперь опиши, как ты поймёшь, что тренировка прошла удачно."
        )

    await send_timeline_event(
        scene="reflect",
        payload={
            "user_id": user_id,
            "chat_id": chat_id,
            "text": user_text,
        },
    )

    await state.set_state(TrainingFlow.reflect)
    await message.answer(reply_text)


# Шаг 3 — финальный переход
@router.message(TrainingFlow.reflect)
async def handle_reflect(message: Message, state: FSMContext):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_text = message.text or ""

    try:
        reply_text = await scene_transition(
            user_id=user_id,
            chat_id=chat_id,
            scene="transition",
        )
    except Exception:
        reply_text = (
            "Переходим к следующему шагу.\n\n"
            "Сделай сегодня один маленький, но реальный шаг в эту сторону."
        )

    await send_timeline_event(
        scene="transition",
        payload={
            "user_id": user_id,
            "chat_id": chat_id,
            "text": user_text,
        },
    )

    await state.clear()
    await message.answer(reply_text, reply_markup=MAIN_MENU)
