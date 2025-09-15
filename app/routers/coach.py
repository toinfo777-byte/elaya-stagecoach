# app/routers/coach.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from datetime import datetime, timezone

from app.bot.states import CoachStates

router = Router(name="coach")


# ===== Вспомогательное =====
def _now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()


async def _mark_feeling_saved(state: FSMContext) -> None:
    """
    Помечаем, что чувство сохранено только что.
    """
    data = await state.get_data()
    data = dict(data or {})
    data["coach_last"] = "feeling_saved"
    data["coach_last_ts"] = _now_ts()
    await state.set_data(data)


async def _recently_saved(state: FSMContext, within: int = 180) -> bool:
    """
    Возвращает True, если чувство сохраняли в пределах `within` секунд.
    """
    data = await state.get_data()
    if not data:
        return False
    ts = data.get("coach_last_ts")
    if not ts:
        return False
    return (_now_ts() - float(ts)) < within and data.get("coach_last") == "feeling_saved"


# ===== Хендлеры коуча =====
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

    # Простая валидация: одно короткое слово
    if not text or len(text.split()) > 2 or len(text) > 32:
        await msg.answer("Одним коротким словом, пожалуйста 🙂")
        return

    # Здесь можно писать в БД/метрики при необходимости
    # save_feeling(user_id=msg.from_user.id, feeling=text)

    await _mark_feeling_saved(state)
    await state.clear()

    await msg.answer("Готово! Сохранил 👍\nЕсли хочешь — начни заново: /coach_on или вернись в меню: /menu")


# ===== Мягкий гард (работает ТОЛЬКО если недавно сохраняли) =====
@router.message(F.text)
async def coach_post_saved_soft_guard(msg: Message, state: FSMContext):
    """
    Отвечаем мягко лишь в течение нескольких минут после сохранения.
    В остальных случаях не мешаем другим роутерам.
    """
    if await _recently_saved(state):
        await msg.answer(
            "Я уже записал твоё ощущение 👌\n"
            "Начать ещё раз — /coach_on, открыть меню — /menu"
        )
        return
    # Если недавно ничего не сохраняли — ничего не делаем:
    # событие уйдёт дальше по другим роутерам (меню, help и т.п.)
