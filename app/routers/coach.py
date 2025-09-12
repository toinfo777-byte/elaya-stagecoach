# app/routers/coach.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta, timezone

from app.bot.states import CoachStates

router = Router(name="coach")

# Хелпер: сохранить «последний шаг коуча выполнен»
async def _mark_feeling_saved(state: FSMContext) -> None:
    data = await state.storage.get_data(bot=state.bot, key=state.key)
    data = dict(data or {})
    data["coach_last"] = "feeling_saved"
    data["coach_last_ts"] = datetime.now(timezone.utc).timestamp()
    await state.storage.set_data(bot=state.bot, key=state.key, data=data)

# Хелпер: проверка — недавно уже сохраняли чувство?
async def _recently_saved(state: FSMContext, within: int = 180) -> bool:
    data = await state.storage.get_data(bot=state.bot, key=state.key)
    ts = (data or {}).get("coach_last_ts")
    if not ts:
        return False
    return (datetime.now(timezone.utc).timestamp() - float(ts)) < within and \
           (data or {}).get("coach_last") == "feeling_saved"

# Старт мини-шага коуча (пример: вы его зовёте в нужном месте вашего сценария)
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

# Принимаем ОДНО слово после таймера
@router.message(CoachStates.wait_feeling, F.text)
async def coach_feeling(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()

    # простая валидация «одно короткое слово»
    if not text or len(text.split()) > 2 or len(text) > 32:
        await msg.answer("Одним коротким словом, пожалуйста 🙂")
        return

    # тут можно сохранить в БД/метрики
    # save_feeling(user_id=msg.from_user.id, feeling=text)  # <-- если нужно

    await _mark_feeling_saved(state)
    await state.clear()

    await msg.answer("Готово! Сохранил 👍\nЕсли хочешь — продолжим или возвращайся в меню: /menu")

# Если пользователь по инерции присылает ещё одно сообщение в течение 3 минут,
# ответим мягко, вместо того чтобы улететь в общий фоллбек.
@router.message(F.text)
async def coach_post_saved_soft_guard(msg: Message, state: FSMContext):
    if await _recently_saved(state):
        await msg.answer(
            "Я уже записал твоё ощущение 👌\n"
            "Начать ещё раз — /coach_on, открыть меню — /menu"
        )
        return
    # Ничего не делаем — пускай обработают остальные роутеры (меню и т.п.)
