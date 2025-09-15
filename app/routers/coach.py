# app/routers/coach.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from datetime import datetime, timezone

from app.bot.states import CoachStates

router = Router(name="coach")

# Помечаем, что чувство сохранено (кладём отметку в FSM-данные)
async def _mark_feeling_saved(state: FSMContext) -> None:
    await state.update_data(
        coach_last="feeling_saved",
        coach_last_ts=datetime.now(timezone.utc).timestamp(),
    )

# Проверяем, что недавно (в пределах within секунд) сохраняли чувство
async def _recently_saved(state: FSMContext, within: int = 180) -> bool:
    data = await state.get_data()
    ts = data.get("coach_last_ts")
    if not ts:
        return False
    return (datetime.now(timezone.utc).timestamp() - float(ts)) < within and \
           data.get("coach_last") == "feeling_saved"

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

    # TODO: сохраните «чувство» при необходимости
    await _mark_feeling_saved(state)

    # Выходим из состояния, НО данные не чистим — отметка останется
    await state.set_state(None)
    await msg.answer("Готово! Сохранил 👍\nЕсли хочешь — начни заново: /coach_on или вернись в меню: /menu")

# Мягкая защита на 3 минуты после сохранения:
# если пользователь по инерции продолжает писать, просто подскажем,
# а все остальные сообщения/кнопки НЕ перехватываем.
@router.message(F.text)
async def coach_post_saved_soft_guard(msg: Message, state: FSMContext):
    # Команды не трогаем — их обработают дальше
    if msg.text and msg.text.startswith("/"):
        return
    # Если недавно сохраняли — мягкое подсказочное сообщение
    if await _recently_saved(state):
        await msg.answer("Я уже записал твоё ощущение 👌\nНачать ещё раз — /coach_on, открыть меню — /menu")
    # Иначе ничего не делаем — пусть обработают остальные роутеры
