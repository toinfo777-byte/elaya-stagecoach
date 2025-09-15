# app/routers/coach.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import SkipHandler
from datetime import datetime, timedelta, timezone

from app.bot.states import CoachStates

router = Router(name="coach")

# --- helpers ---------------------------------------------------------------

async def _mark_feeling_saved(state: FSMContext) -> None:
    data = await state.storage.get_data(bot=state.bot, key=state.key)
    data = dict(data or {})
    data["coach_last"] = "feeling_saved"
    data["coach_last_ts"] = datetime.now(timezone.utc).timestamp()
    await state.storage.set_data(bot=state.bot, key=state.key, data=data)

async def _recently_saved(state: FSMContext, within: int = 180) -> bool:
    data = await state.storage.get_data(bot=state.bot, key=state.key)
    ts = (data or {}).get("coach_last_ts")
    if not ts:
        return False
    fresh = (datetime.now(timezone.utc).timestamp() - float(ts)) < within
    return fresh and (data or {}).get("coach_last") == "feeling_saved"

# --- flow ------------------------------------------------------------------

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

    # тут можно сохранить в БД/метрики
    await _mark_feeling_saved(state)
    await state.clear()

    await msg.answer("Готово! Сохранил 👍\nЕсли хочешь — начни заново: /coach_on или вернись в меню: /menu")

# ВАЖНО: этот обработчик НЕ должен «съедать» все сообщения.
@router.message(F.text)
async def coach_post_saved_soft_guard(msg: Message, state: FSMContext):
    if await _recently_saved(state):
        await msg.answer(
            "Я уже записал твоё ощущение 👌\n"
            "Начать ещё раз — /coach_on, открыть меню — /menu"
        )
        return
    # пропускаем дальше к остальным роутерам (меню/шорткаты и т.д.)
    raise SkipHandler()
