# trainer/app/routes/training.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from app.core_api import scene_enter, scene_reflect, scene_transition
from app.elaya_core import send_timeline_event

router = Router(name="training")


class TrainingFlow(StatesGroup):
    intro = State()
    reflect = State()
    transition = State()


# 🚀 Вход в "Тренировку дня"
# 1) команда /training
# 2) кнопка/фраза "Тренировка дня"
@router.message(Command("training"))
@router.message(F.text.lower().contains("тренировка дня"))
async def start_training(message: Message, state: FSMContext) -> None:
    """
    Старт тренировки:
    - дергаем старое ядро через scene_enter (если настроено CORE_API_BASE)
    - отправляем событие intro в новое ядро Элайи
    - ставим состояние intro
    """
    user_id = message.from_user.id if message.from_user else 0
    chat_id = message.chat.id

    # 1) старый core_api (опционально, если у тебя настроен CORE_API_BASE)
    try:
        reply_text = await scene_enter(
            user_id=user_id,
            chat_id=chat_id,
            scene="intro",
        )
    except Exception:
        # fallback, если старое ядро не отвечает
        reply_text = (
            "Привет! Я Элайя — тренер сцены.\n\n"
            "Помогу прокачать голос, дыхание, уверенность и выразительность.\n"
            "Напиши пару слов о своём состоянии или запросе перед тренировкой."
        )

    # 2) новое ядро Элайи — событие intro
    await send_timeline_event(
        "intro",
        {
            "user_id": user_id,
            "chat_id": chat_id,
            "text": "trainer intro started",
        },
    )

    await state.set_state(TrainingFlow.intro)
    await message.answer(reply_text, reply_markup=ReplyKeyboardRemove())


# 🪞 Фаза reflect — пользователь пишет текст
@router.message(TrainingFlow.intro)
async def handle_reflect(message: Message, state: FSMContext) -> None:
    """
    Пользователь отвечает после вступления.
    Это уходит:
    - в старое ядро через scene_reflect (если нужно)
    - в новое ядро как событие reflect
    """
    user_id = message.from_user.id if message.from_user else 0
    chat_id = message.chat.id
    user_text = message.text or ""

    # 1) старое ядро (опционально)
    try:
        reply_text = await scene_reflect(
            user_id=user_id,
            chat_id=chat_id,
            scene="reflect",
            text=user_text,
        )
    except Exception:
        reply_text = (
            "Я услышала тебя.\n"
            "Сейчас мы сделаем небольшой переход к практике.\n\n"
            "Когда будешь готов — напиши: «Дальше»."
        )

    # 2) новое ядро — событие reflect
    await send_timeline_event(
        "reflect",
        {
            "user_id": user_id,
            "chat_id": chat_id,
            "text": user_text,
        },
    )

    await state.set_state(TrainingFlow.reflect)
    await message.answer(reply_text)


# 🔁 Фаза transition — переход к упражнению / завершению
@router.message(TrainingFlow.reflect)
async def handle_transition(message: Message, state: FSMContext) -> None:
    """
    Переходная фаза:
    - фиксация результата отражения
    - событие transition в ядро
    """
    user_id = message.from_user.id if message.from_user else 0
    chat_id = message.chat.id
    user_text = message.text or ""

    # 1) старое ядро (опционально)
    try:
        reply_text = await scene_transition(
            user_id=user_id,
            chat_id=chat_id,
            scene="transition",
        )
    except Exception:
        reply_text = (
            "Переходим к следующему шагу.\n\n"
            "На сегодня этого достаточно. "
            "Если захочешь продолжить — снова нажми «Тренировка дня»."
        )

    # 2) новое ядро — событие transition
    await send_timeline_event(
        "transition",
        {
            "user_id": user_id,
            "chat_id": chat_id,
            "text": user_text,
        },
    )

    await state.clear()
    await message.answer(reply_text)
