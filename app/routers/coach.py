# app/routers/coach.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router(name="coach")

class CoachStates(StatesGroup):
    wait_feeling = State()

@router.message(F.text == "/coach_on")
async def coach_on(msg: Message, state: FSMContext):
    await msg.answer(
        "Коротко: попробуй это — Пауза как правда (4-2-6-2).\n"
        "Шаги: Вдох 4 → Пауза 2 → Выдох 6 → Пауза 2.\n"
        "Признак: Что произошло после паузы?\n"
        "Запусти таймер и отметь ощущение одним словом.\n\n"
        "⏱ Таймер 60 сек"
    )
    await state.set_state(CoachStates.wait_feeling)

@router.message(CoachStates.wait_feeling, F.text)
async def coach_feeling(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()
    if not text or len(text.split()) > 2 or len(text) > 32:
        await msg.answer("Одним коротким словом, пожалуйста 🙂")
        return

    # save_feeling(user_id=msg.from_user.id, feeling=text)  # если нужно
    await state.clear()
    await msg.answer("Готово! Сохранил 👍\nЕсли хочешь — начни заново: /coach_on или вернись в меню: /menu")
