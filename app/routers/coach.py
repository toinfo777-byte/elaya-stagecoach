# app/routers/coach.py
from datetime import datetime, timezone

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.bot.states import CoachStates

router = Router(name="coach")

# ===== Хелперы =====

_RECENT_WINDOW_SEC = 180  # 3 мин — окно, в которое мягко игнорим повторные ответы


async def _mark_feeling_saved(state: FSMContext) -> None:
    """
    Отмечаем, что шаг коуча успешно выполнен недавно.
    В aiogram v3 работаем напрямую через FSMContext.
    """
    now_ts = int(datetime.now(timezone.utc).timestamp())
    # частичное обновление данных состояния
    await state.update_data(
        coach_last="feeling_saved",
        coach_last_ts=now_ts,
    )


async def _recently_saved(state: FSMContext, within: int = _RECENT_WINDOW_SEC) -> bool:
    """
    True, если в пределах окна already saved.
    """
    data = await state.get_data()
    ts = data.get("coach_last_ts")
    if not ts:
        return False
    now_ts = int(datetime.now(timezone.utc).timestamp())
    return (now_ts - int(ts)) < within and data.get("coach_last") == "feeling_saved"


# ===== Хэндлеры =====

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

    # тут можно сохранить в БД/метрики
    # save_feeling(user_id=msg.from_user.id, feeling=text)

    await _mark_feeling_saved(state)
    await state.clear()

    await msg.answer("Готово! Сохранил 👍\nЕсли хочешь — продолжим или возвращайся в меню: /menu")


# Мягкий гард: если юзер прислал ещё сообщение в течение окна после сохранения,
# отвечаем мягко, а не валимся в общий фолбэк.
@router.message(F.text)
async def coach_post_saved_soft_guard(msg: Message, state: FSMContext):
    if await _recently_saved(state):
        await msg.answer(
            "Я уже записал твоё ощущение 👌\n"
            "Начать ещё раз — /coach_on, открыть меню — /menu"
        )
        return
    # Ничего не делаем — другие роутеры (меню и т.п.) подхватят
