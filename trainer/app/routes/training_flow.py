# trainer/app/routes/training_flow.py
from __future__ import annotations

from datetime import date
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU, BTN_TRAINING
from app.training_progress import register_training
from app.core_client import send_timeline_event


router = Router()
logger = logging.getLogger(__name__)


ERROR_FALLBACK_TEXT = (
    "Похоже, что-то пошло не так на стороне сервера.\n"
    "Я уже отметил это в журнале.\n\n"
    "Попробуй ещё раз через пару минут или напиши в Штаб."
)


# ---------------------------------------------------------------------------
# FSM STATES
# ---------------------------------------------------------------------------


class TrainingFlow(StatesGroup):
    vector = State()
    reflect = State()
    transition = State()
    review = State()


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------


@router.message(F.text == BTN_TRAINING)
async def handle_training_entry(message: Message, state: FSMContext) -> None:
    """
    Точка входа в тренировку — срабатывает на кнопку «🎭 Тренировка дня».
    """
    await start_training(message, state)


async def start_training(message: Message, state: FSMContext) -> None:
    """
    Старт тренировки:
    1) отправляем событие в таймлайн,
    2) переводим FSM в состояние vector,
    3) задаём первый вопрос.
    """
    try:
        await send_timeline_event(
            scene="trainer.day.start",
            payload={
                "tg_user_id": message.from_user.id,
            },
        )
    except Exception as e:
        # Не ломаем тренировку, просто логируем
        logger.exception("Failed to send trainer.day.start: %s", e)

    await state.set_state(TrainingFlow.vector)
    await message.answer(
        "Старт тренировки дня.\n\n"
        "1️⃣ Коротко напиши — в каком состоянии ты входишь в день.\n"
        "Что сейчас главное в тебе / в поле?"
    )


# ---------------------------------------------------------------------------
# QUESTION 1 — VECTOR
# ---------------------------------------------------------------------------


@router.message(TrainingFlow.vector)
async def handle_vector(message: Message, state: FSMContext) -> None:
    """
    Первый вопрос: состояние / вектор.
    """
    await state.update_data(vector=(message.text or "").strip())

    await state.set_state(TrainingFlow.reflect)
    await message.answer(
        "2️⃣ Как ты видишь свой день со стороны?\n"
        "Каким он может быть, если ты будешь в присутствии?"
    )


# ---------------------------------------------------------------------------
# QUESTION 2 — REFLECT
# ---------------------------------------------------------------------------


@router.message(TrainingFlow.reflect)
async def handle_reflect(message: Message, state: FSMContext) -> None:
    """
    Второй вопрос: взгляд со стороны.
    """
    await state.update_data(reflect=(message.text or "").strip())

    await state.set_state(TrainingFlow.transition)
    await message.answer(
        "3️⃣ Какой один маленький шаг ты готов сделать сегодня,\n"
        "чтобы поддержать это состояние и этот день?"
    )


# ---------------------------------------------------------------------------
# QUESTION 3 — TRANSITION
# ---------------------------------------------------------------------------


@router.message(TrainingFlow.transition)
async def handle_transition(message: Message, state: FSMContext) -> None:
    """
    Третий вопрос: шаг / действие.
    """
    await state.update_data(transition=(message.text or "").strip())

    await state.set_state(TrainingFlow.review)
    await message.answer(
        "📝 Если хочешь, напиши пару слов о том,\n"
        "как тебе сама настройка / тренировка.\n\n"
        "Можно просто отправить любой текст — даже один смайлик 🙂"
    )


# ---------------------------------------------------------------------------
# FINAL STEP — REVIEW + SAVE + TIMELINE
# ---------------------------------------------------------------------------


@router.message(TrainingFlow.review)
async def handle_review(message: Message, state: FSMContext) -> None:
    """
    Финальный шаг:
    - забираем все данные из FSM,
    - сохраняем тренировку локально,
    - отправляем событие в таймлайн,
    - очищаем состояние и возвращаем главное меню.
    """
    try:
        review = (message.text or "").strip()
        data = await state.get_data()

        # Сохранение полной тренировки (локальное in-memory хранилище)
        register_training(
            user_id=message.from_user.id,
            date=date.today(),
            vector=data.get("vector", ""),
            reflect=data.get("reflect", ""),
            transition=data.get("transition", ""),
            review=review,
        )

        # Таймлайн: завершение дня
        try:
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
        except Exception as e:
            # Не роняем диалог из-за ядра
            logger.exception("Failed to send trainer.day.finish: %s", e)

        # Завершаем FSM
        await state.clear()

        await message.answer(
            "Хорошая работа. Я сохранил твою тренировку.\n"
            "Если захочешь — нажимай «🎭 Тренировка дня».",
            reply_markup=MAIN_MENU,
        )

    except Exception as e:
        logger.exception("Trainer review error: %s", e)
        await state.clear()
        await message.answer(
            ERROR_FALLBACK_TEXT,
            reply_markup=MAIN_MENU,
        )
