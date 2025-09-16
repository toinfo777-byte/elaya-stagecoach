# app/bot/handlers/feedback.py
from __future__ import annotations

import logging
import re
from typing import Optional

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
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

# ---------- эвристики распознавания из callback_data ----------

_RE_NUM = re.compile(r"(?<!\d)([123])(?!\d)")

def _norm(s: str | None) -> str:
    return (s or "").strip().lower()

def _detect_phrase_by_data(data: str) -> bool:
    s = _norm(data)
    return any(k in s for k in (
        "fb:phrase", "phrase", "one_phrase", "comment", "review", "note", "text",
        "фраз", "текст",
    ))

def _detect_rate_by_data(data: str) -> Optional[str]:
    s = _norm(data)

    # слова/эмодзи
    if any(k in s for k in ("rate:hot", "fb:hot", "hot", "fire", "🔥", "r_hot", "rate-hot")):
        return "hot"
    if any(k in s for k in ("rate:ok", "fb:ok", "ok", "👌", "thumb", "👍", "good")):
        return "ok"
    if any(k in s for k in ("rate:meh", "fb:meh", "meh", "neutral", "😐", "so_so", "bad")):
        return "meh"

    # числа/коды
    m = _RE_NUM.search(s)
    if m:
        return {"1": "hot", "2": "ok", "3": "meh"}.get(m.group(1))

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

# ---------- fallback: определяем по клавиатуре (текст/позиция) ----------

def _detect_rate_by_markup(cq: CallbackQuery) -> Optional[str]:
    rm: InlineKeyboardMarkup | None = getattr(getattr(cq, "message", None), "reply_markup", None)
    if not rm or not isinstance(rm, InlineKeyboardMarkup):
        return None

    for r_idx, row in enumerate(rm.inline_keyboard or []):
        for c_idx, btn in enumerate(row or []):
            if not isinstance(btn, InlineKeyboardButton):
                continue
            if btn.callback_data == cq.data:
                txt = (btn.text or "").strip()
                # по тексту кнопки
                if "🔥" in txt or "огонь" in txt.lower():
                    return "hot"
                if "👌" in txt or "👍" in txt or "ok" in txt.lower():
                    return "ok"
                if "😐" in txt or "нейтр" in txt.lower():
                    return "meh"
                # по позиции (первая строка: 0/1/2)
                if r_idx == 0 and c_idx in (0, 1, 2):
                    return {0: "hot", 1: "ok", 2: "meh"}[c_idx]
                # ничего не распознали
                return None
    return None

def _is_phrase_button_by_markup(cq: CallbackQuery) -> bool:
    rm: InlineKeyboardMarkup | None = getattr(getattr(cq, "message", None), "reply_markup", None)
    if not rm or not isinstance(rm, InlineKeyboardMarkup):
        return False
    for row in rm.inline_keyboard or []:
        for btn in row or []:
            if getattr(btn, "callback_data", None) == cq.data:
                txt = (btn.text or "").lower()
                return any(k in txt for k in ("фраз", "phrase", "comment", "review", "text"))
    return False

# ----------------------------- обработчики -----------------------------

@router.callback_query()
async def feedback_any(cq: CallbackQuery, state: FSMContext):
    data = cq.data or ""
    try:
        log.info("FB callback user=%s data=%r", getattr(cq.from_user, "id", "?"), data)
    except Exception:
        pass

    # 1) «фраза»
    if _detect_phrase_by_data(data) or _is_phrase_button_by_markup(cq):
        await state.set_state(FeedbackStates.wait_phrase)
        await cq.answer()  # просто погасить крутилку
        await cq.message.answer(PROMPT_TEXT)
        return

    # 2) оценка
    rate = _detect_rate_by_data(data) or _detect_rate_by_markup(cq)
    if rate:
        # TODO: сохранить оценку (rate) в БД
        await cq.answer(RATE_ALERT_TEXT.get(rate, "Принято"), show_alert=False)
        return

    # 3) прочее — тихо подтверждаем
    await cq.answer()  # без текста


@router.message(FeedbackStates.wait_phrase, ~F.text.startswith("/"))
async def fb_phrase_text(msg: Message, state: FSMContext):
    phrase = (msg.text or "").strip()
    # TODO: сохранить phrase в БД
    await state.clear()
    await msg.answer("Спасибо! Принял ✍️")

@router.message(FeedbackStates.wait_phrase, Command("cancel"))
async def fb_phrase_cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Отменил. Если что — нажмите «✍ 1 фраза» ещё раз.")
