# app/bot/handlers/feedback.py
from __future__ import annotations

import logging
import re
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from app.bot.states import FeedbackStates

router = Router(name="feedback2")
log = logging.getLogger(__name__)

PROMPT_TEXT = (
    "Напишите одну короткую фразу об этом этюде. "
    "Если передумали — отправьте /cancel."
)

RATE_ALERT_TEXT = {
    "hot": "🔥 Принял. Спасибо!",
    "ok":  "👌 Принял. Спасибо!",
    "meh": "😐 Принял. Спасибо!",
}

# ---------- эвристики распознавания действий из callback_data ----------

_RE_NUM = re.compile(r"(?<!\d)([123])(?!\d)")  # одиночные цифры 1/2/3 без соседних цифр

def _norm(s: str | None) -> str:
    return (s or "").strip().lower()

def _detect_phrase(data: str) -> bool:
    s = _norm(data)
    return any(k in s for k in (
        "fb:phrase", "phrase", "one_phrase", "comment", "review", "note", "text",
        "фраз", "текст",
    ))

def _detect_rate(data: str) -> str | None:
    s = _norm(data)

    # явные слова/эмодзи
    if any(k in s for k in ("rate:hot", "fb:hot", "hot", "fire", "🔥", "r_hot", "rate-hot")):
        return "hot"
    if any(k in s for k in ("rate:ok", "fb:ok", "ok", "👌", "thumb", "👍", "good")):
        return "ok"
    if any(k in s for k in ("rate:meh", "fb:meh", "meh", "neutral", "😐", "so_so", "bad")):
        return "meh"

    # числовые коды
    m = _RE_NUM.search(s)
    if m:
        # 1 = hot, 2 = ok, 3 = meh — самая частая мапа
        return {"1": "hot", "2": "ok", "3": "meh"}.get(m.group(1))

    # альтернативные форматы r1, r_2, rate_3, fb-2 и т.п.
    for pat, val in (
        (r"(?:^|[^a-z])r[:_\-]?1(?!\d)", "hot"),
        (r"(?:^|[^a-z])r[:_\-]?2(?!\d)", "ok"),
        (r"(?:^|[^a-z])r[:_\-]?3(?!\d)", "meh"),
        (r"rate[:_\-]?1(?!\d)", "hot"),
        (r"rate[:_\-]?2(?!\d)", "ok"),
        (r"rate[:_\-]?3(?!\d)", "meh"),
        (r"fb[:_\-]?1(?!\d)", "hot"),
        (r"fb[:_\-]?2(?!\d)", "ok"),
        (r"fb[:_\-]?3(?!\d)", "meh"),
    ):
        if re.search(pat, s):
            return val

    return None

# ----------------------------- обработчики -----------------------------

@router.callback_query()
async def universal_feedback_handler(cq: CallbackQuery, state: FSMContext):
    """Единая точка входа: распознаём действие и отвечаем.
    НИКОГДА не оставляем крутилку висеть.
    """
    data = cq.data or ""
    try:
        log.info("FB callback from %s: %r", getattr(cq.from_user, "id", "?"), data)
    except Exception:
        pass

    # 0) мгновенно гасим крутилку
    try:
        await cq.answer("Ок")
    except Exception:
        pass

    # 1) фраза?
    if _detect_phrase(data):
        await state.set_state(FeedbackStates.wait_phrase)
        await cq.message.answer(PROMPT_TEXT)
        return

    # 2) оценка?
    rate = _detect_rate(data)
    if rate:
        # TODO: здесь можно сохранить оценку в БД
        try:
            await cq.answer(RATE_ALERT_TEXT.get(rate, "Принято"), show_alert=False)
        except Exception:
            # тост мог уже быть, это не критично
            pass
        return

    # 3) неизвестная кнопка — спокойно подтверждаем
    # (доп. действий не требуется)
    return


@router.message(FeedbackStates.wait_phrase, ~F.text.startswith("/"))
async def fb_phrase_text(msg: Message, state: FSMContext):
    phrase = (msg.text or "").strip()
    # TODO: сохранить phrase в БД, привязав к текущему этюду/пользователю
    await state.clear()
    await msg.answer("Спасибо! Принял ✍️")


@router.message(FeedbackStates.wait_phrase, Command("cancel"))
async def fb_phrase_cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Отменил. Если что — нажмите «✍ 1 фраза» ещё раз.")
