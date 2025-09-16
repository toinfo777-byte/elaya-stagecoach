# app/bot/handlers/feedback.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

# если у вас класс уже лежит в app/bot/states.py — импортируем отсюда
from app.bot.states import FeedbackStates

router = Router(name="feedback2")

# ---- Тексты (можете подправить под себя) ----
PROMPT_TEXT = (
    "Напишите одну короткую фразу об этом этюде. "
    "Если передумали — отправьте /cancel."
)

RATE_ALERT_TEXT = {
    "hot": "🔥 Принял. Спасибо!",
    "ok": "👌 Принял. Спасибо!",
    "meh": "😐 Принял. Спасибо!",
}

# ============================================================
# Универсальный парсер оценок из callback_data
# Поддерживает разные форматы и эмодзи:
#   'rate:hot', 'fb:hot', 'hot', 'fire', '🔥'
#   'rate:ok', 'ok', '👌', 'thumb', '👍'
#   'rate:meh', 'meh', 'neutral', '😐'
# ============================================================
def parse_rate_from_cb(data: str | None) -> str | None:
    if not data:
        return None
    s = data.lower()

    # горячо
    if any(t in s for t in ("rate:hot", "fb:hot", "hot", "fire", "🔥")):
        return "hot"

    # норм / ок
    if any(t in s for t in ("rate:ok", "fb:ok", "ok", "👌", "thumb", "👍")):
        return "ok"

    # так себе / нейтрально
    if any(t in s for t in ("rate:meh", "fb:meh", "meh", "neutral", "😐")):
        return "meh"

    return None


# «эта кнопка — про фразу?»
def _is_phrase_cb(data: str | None) -> bool:
    if not data:
        return False
    s = data.lower()
    # любые варианты: 'phrase', 'fb:phrase', 'one_phrase', рус. корень «фраз»
    return any(t in s for t in ("phrase", "one_phrase", "fb:phrase", "фраз"))


# ============================================================
# ОЦЕНКИ — inline кнопки
# ============================================================
@router.callback_query(F.data.func(lambda d: parse_rate_from_cb(d) is not None))
async def fb_rate_inline(cq: CallbackQuery):
    # 1) Мгновенный ответ, чтобы не висела крутилка
    try:
        await cq.answer("Принято")
    except Exception:
        pass

    # 2) Бизнес-логика
    code = parse_rate_from_cb(cq.data)
    txt = RATE_ALERT_TEXT.get(code, "Принято")

    # TODO: Сохранить оценку в БД, если нужно
    # Пример:
    #   with session_scope() as s:
    #       save_run_rate(user_id=cq.from_user.id, run_id=..., rate=code)

    # 3) Небольшой тост (по желанию)
    try:
        await cq.answer(txt, show_alert=False)
    except Exception:
        pass


# ============================================================
# «✍ 1 фраза» — inline кнопка
# ============================================================
@router.callback_query(F.data.func(_is_phrase_cb))
async def fb_phrase_inline(cq: CallbackQuery, state: FSMContext):
    # 1) мгновенный ответ
    try:
        await cq.answer("Ок")
    except Exception:
        pass

    # 2) переводим в состояние и даём подсказку
    await state.set_state(FeedbackStates.wait_phrase)
    await cq.message.answer(PROMPT_TEXT)


# Принимаем фразу в состоянии
@router.message(FeedbackStates.wait_phrase, ~F.text.startswith("/"))
async def fb_phrase_text(msg: Message, state: FSMContext):
    phrase = (msg.text or "").strip()

    # TODO: Сохранить фразу в БД/журнал (привязав к текущему этюду/дате/пользователю)
    # Пример:
    #   with session_scope() as s:
    #       save_run_phrase(user_id=msg.from_user.id, run_id=..., phrase=phrase)

    await state.clear()
    await msg.answer("Спасибо! Принял ✍️")


# Отмена набора фразы
@router.message(FeedbackStates.wait_phrase, Command("cancel"))
async def fb_phrase_cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Отменил. Если что — можете нажать «✍ 1 фраза» ещё раз.")


# ============================================================
# Fallback на все прочие callback-и
# (Чтобы крутилка НИКОГДА не зависала)
# ============================================================
@router.callback_query()
async def cb_fallback_ok(cq: CallbackQuery):
    try:
        await cq.answer("Ок")
    except Exception:
        pass
