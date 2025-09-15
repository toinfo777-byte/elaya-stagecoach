# app/routers/coach.py
from datetime import datetime, timedelta, timezone

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.bot.states import CoachStates

router = Router(name="coach")


def _utc_ts() -> float:
    return datetime.now(timezone.utc).timestamp()


# ===== helpers ===============================================================

async def _mark_feeling_saved(state: FSMContext) -> None:
    """
    Отмечаем, что шаг коуча выполнен недавно (без обращения к state.bot).
    """
    # get_data/update_data — корректные методы для Aiogram 3
    data = await state.get_data()
    data = dict(data or {})
    data["coach_last"] = "feeling_saved"
    data["coach_last_ts"] = _utc_ts()
    await state.update_data(**data)


async def _recently_saved(state: FSMContext, within_sec: int = 180) -> bool:
    """
    Проверяем, сохраняли ли чувство в последние within_sec секунд.
    """
    data = await state.get_data()
    if not data:
        return False
    ts = float(data.get("coach_last_ts") or 0)
    if not ts:
        return False
    is_recent = (_utc_ts() - ts) < within_sec
    return is_recent and data.get("coach_last") == "feeling_saved"


# ===== handlers ==============================================================

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

    # простая валидация «одно короткое слово»
    if not text or len(text.split()) > 2 or len(text) > 32:
        await msg.answer("Одним коротким словом, пожалуйста 🙂")
        return

    # тут можно сохранить в БД/метрики, если нужно
    # save_feeling(user_id=msg.from_user.id, feeling=text)

    await _mark_feeling_saved(state)
    await state.clear()
    await msg.answer("Готово! Сохранил 👍\nЕсли хочешь — начни заново: /coach_on или вернись в меню: /menu")


# Мягкий ответ только на ПЛОСКИЙ текст (не команды), если недавно уже сохранили
@router.message(F.text & ~F.text.startswith("/"))
async def coach_post_saved_soft_guard(msg: Message, state: FSMContext):
    if await _recently_saved(state):
        await msg.answer(
            "Я уже записал твоё ощущение 👌\n"
            "Начать ещё раз — /coach_on, открыть меню — /menu"
        )
        return
    # иначе не вмешиваемся — дальше обработают другие роутеры
