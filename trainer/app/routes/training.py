# trainer/app/routes/training.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from app.elaya_core import send_timeline_event
from app.keyboards.main_menu import MAIN_MENU

router = Router(name="training")


class TrainingFlow(StatesGroup):
    intro = State()
    reflect = State()
    finish = State()


# 🚀 Вход в "Тренировку дня"
# 1) запасной вход: команда /training
# 2) основной вход: нажатие кнопки "🏋️‍♂️ Тренировка дня"
@router.message(Command("training"))
@router.message(F.text.contains("Тренировка дня"))
async def training_entry(message: Message, state: FSMContext) -> None:
    # фиксируем событие в ядре
    await send_timeline_event(
        scene="training_day_start",
        payload={
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "full_name": message.from_user.full_name,
        },
    )

    await state.set_state(TrainingFlow.intro)

    text = (
        "🟣 Стартуем тренировку дня.\n\n"
        "1. Встань или сядь ровно.\n"
        "2. Сделай 3 спокойных цикла дыхания: вдох 4с — выдох 6с.\n"
        "3. На выдохе отметь, как опускается напряжение.\n\n"
        "Когда будешь готов — напиши мне одно слово: <b>Готов</b>."
    )

    await message.answer(text)


# 🧩 Рефлексия после первой фазы
@router.message(TrainingFlow.intro, F.text.func(lambda t: t and "готов" in t.lower()))
async def training_reflect(message: Message, state: FSMContext) -> None:
    await send_timeline_event(
        scene="training_day_phase1_done",
        payload={
            "user_id": message.from_user.id,
            "text": message.text,
        },
    )

    await state.set_state(TrainingFlow.reflect)

    text = (
        "Отлично 💫\n\n"
        "Теперь короткая рефлексия:\n"
        "— что изменилось в теле за эти 3 цикла?\n"
        "— стало ли дыхание свободнее?\n\n"
        "Ответь парой фраз — как чувствуешь."
    )
    await message.answer(text)


@router.message(TrainingFlow.reflect)
async def training_finish(message: Message, state: FSMContext) -> None:
    await send_timeline_event(
        scene="training_day_finish",
        payload={
            "user_id": message.from_user.id,
            "reflection": message.text,
        },
    )

    await state.clear()

    text = (
        "Спасибо, тренировка зафиксирована ✅\n\n"
        "Если захочешь — можешь запустить её снова через кнопку "
        "«🏋️‍♂️ Тренировка дня» или команду /training.\n\n"
        "Главное меню всегда доступно снизу."
    )

    await message.answer(text, reply_markup=MAIN_MENU)
