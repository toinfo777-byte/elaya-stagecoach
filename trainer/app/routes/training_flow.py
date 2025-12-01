# trainer/app/routes/training_flow.py
from __future__ import annotations

import logging
from datetime import date

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU
from app.core_api import safe_timeline
from app.training_progress import (
    register_training,
    register_training_simple,
)

router = Router(name="training")

# пока один пользователь
USER_ID = 1

# текст кнопки тренировки в главном меню
BTN_TRAINING_TEXT = "🎭 Тренировка дня"


# ================================
#   FSM СЦЕНАРИЙ ТРЕНИРОВКИ ДНЯ
# ================================
class TrainingFlow(StatesGroup):
    vector = State()      # состояние входа: настроение / вектор дня
    reflect = State()     # что было ярким/главным
    transition = State()  # куда направляем шаг
    review = State()      # мини-отзыв фразой


# ================================
#   /START → ГЛАВНОЕ МЕНЮ
# ================================
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """
    Старт бота: очищаем состояние и показываем главное меню.
    """
    await state.clear()

    await message.answer(
        "Привет. Это Элайя-Тренер.\n\n"
        "Когда почувствуешь — нажимай «🎭 Тренировка дня».\n"
        "Я рядом.",
        reply_markup=MAIN_MENU,
    )


# ================================
#   ЗАПУСК ТРЕНИРОВКИ
# ================================
@router.message(Command("training"))
@router.message(F.text == BTN_TRAINING_TEXT)
async def start_training(message: Message, state: FSMContext) -> None:
    """
    Старт тренировочного процесса.
    """
    await state.clear()
    await state.set_state(TrainingFlow.vector)

    # событие старта тренировки
    await safe_timeline("trainer:start", {"user_id": USER_ID})

    await message.answer(
        "🎭 <b>Старт тренировки дня</b>\n\n"
        "Коротко напиши — в каком состоянии ты входишь в день.\n"
        "Одно слово или короткая фраза.",
    )


# ================================
#   ШАГ 1 — ВХОДНОЙ ВЕКТОР
# ================================
@router.message(TrainingFlow.vector)
async def handle_vector(message: Message, state: FSMContext) -> None:
    """
    Сохраняем входной вектор и переходим к отражению дня.
    """
    vector = (message.text or "").strip()

    await state.update_data(vector=vector)
    await state.set_state(TrainingFlow.reflect)

    await message.answer(
        "🟣 Шаг 2.\n"
        "Что было самым ярким или важным сегодня?",
    )


# ================================
#   ШАГ 2 — ОТРАЖЕНИЕ ДНЯ
# ================================
@router.message(TrainingFlow.reflect)
async def handle_reflect(message: Message, state: FSMContext) -> None:
    """
    Фиксируем главное/яркое за день и переходим к шагу на завтра.
    """
    reflect = (message.text or "").strip()

    await state.update_data(reflect=reflect)
    await state.set_state(TrainingFlow.transition)

    # событие «отражение дня»
    await safe_timeline(
        "trainer:reflect",
        {
            "user_id": USER_ID,
            "reflect": reflect,
        },
    )

    await message.answer(
        "🟣 Шаг 3.\n"
        "Сделай один маленький шаг, который поддержит тебя завтра.\n"
        "Опиши его коротко.",
    )


# ================================
#   ШАГ 3 — ПЕРЕХОД / ШАГ НА ЗАВТРА
# ================================
@router.message(TrainingFlow.transition)
async def handle_transition(message: Message, state: FSMContext) -> None:
    """
    Сохраняем маленький шаг на завтра и переходим к финальному отзыву.
    """
    transition = (message.text or "").strip()

    await state.update_data(transition=transition)
    await state.set_state(TrainingFlow.review)

    # событие «переход / шаг»
    await safe_timeline(
        "trainer:transition",
        {
            "user_id": USER_ID,
            "transition": transition,
        },
    )

    await message.answer(
        "🟣 Финальный шаг.\n"
        "Напиши одну фразу о том, как прошла тренировка.\n"
        "Например: «стало спокойнее», «прояснилось», «сложно, но лучше».\n\n"
        "Это поможет формировать более точный ритм.",
    )


# ================================
#   ФИНАЛ — МИНИ-ОТЗЫВ
# ================================
@router.message(TrainingFlow.review)
async def handle_review(message: Message, state: FSMContext) -> None:
    """
    Сохраняем тренировку, отправляем события в ядро и возвращаем в меню.
    """
    review = (message.text or "").strip()
    data = await state.get_data()

    # --- Сохраняем тренировку в файл ---
    try:
        register_training(
            user_id=USER_ID,
            date=date.today(),
            vector=data.get("vector", ""),
            reflect=data.get("reflect", ""),
            transition=data.get("transition", ""),
            review=review,
        )
    except Exception as e:
        logging.error(f"register_training failed: {e!r}")

    # --- старая in-memory статистика ---
    try:
        await register_training_simple(USER_ID)
    except Exception as e:
        logging.error(f"register_training_simple failed: {e!r}")

    # --- события финала тренировки ---
    await safe_timeline(
        "trainer:review",
        {
            "user_id": USER_ID,
            "vector": data.get("vector", ""),
            "reflect": data.get("reflect", ""),
            "transition": data.get("transition", ""),
            "review": review,
        },
    )

    await safe_timeline(
        "trainer:done",
        {
            "user_id": USER_ID,
        },
    )

    # --- Сбрасываем FSM ---
    await state.clear()

    # --- Финальное сообщение + главное меню ---
    await message.answer(
        "✅ Тренировка завершена.\n"
        "Я сохранил твою тренировку и маленький шаг на завтра.\n\n"
        "Если захочешь — в любой момент нажимай «🎭 Тренировка дня» "
        "в главном меню.",
        reply_markup=MAIN_MENU,
    )
