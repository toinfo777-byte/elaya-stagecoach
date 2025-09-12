# app/bot/handlers/feedback.py
from __future__ import annotations
import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.bot.states import FeedbackStates
from app.bot.keyboards.feedback import feedback_inline_kb

log = logging.getLogger("feedback2")
router = Router(name="feedback2")


# ---- helpers -------------------------------------------------
def _parse_rate(data: str | None) -> str | None:
    if not data:
        return None
    # принимаем любые варианты: "fb:rate:hot", "feedback:rate:ok", "rate:meh"
    if ":rate:" in data:
        return data.split(":")[-1]
    if data.startswith("rate:") and data.count(":") == 1:
        return data.split(":")[1]
    return None

def _is_text_cb(data: str | None) -> bool:
    if not data:
        return False
    # "fb:text", "feedback:text", "text_feedback", любые *:text
    return data.endswith(":text") or data in {"fb:text", "feedback:text", "text_feedback"}


# ---- обработчики ---------------------------------------------
@router.callback_query(F.data.func(lambda d: _parse_rate(d) is not None))
async def on_feedback_rate(cq: CallbackQuery, state: FSMContext):
    # логируем, чтобы видеть в логах факт нажатия
    log.info("feedback rate click: %s", cq.data)
    try:
        await cq.answer("Спасибо за отзыв! 👍", show_alert=False)
    except Exception:
        pass
    try:
        await cq.message.answer("Принято. Спасибо! 🙌")
    except Exception:
        pass


@router.callback_query(F.data.func(_is_text_cb))
async def on_feedback_text_request(cq: CallbackQuery, state: FSMContext):
    log.info("feedback text requested: %s", cq.data)
    try:
        await state.set_state(FeedbackStates.wait_text)
        await cq.answer()
        await cq.message.answer("Напишите короткую фразу-отзыв одним сообщением.")
    except Exception:
        pass


@router.message(FeedbackStates.wait_text)
async def on_feedback_text_submit(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()
    if not text:
        await msg.answer("Пришлите, пожалуйста, обычный текст без вложений.")
        return
    log.info("feedback text received: %s", text)
    await state.clear()
    await msg.answer("Спасибо! Ваш отзыв сохранён. 🙏")


# Фолбэк: если вдруг прилетит любой колбэк, начинающийся с fb:
@router.callback_query(F.data.func(lambda d: isinstance(d, str) and d.startswith("fb:")))
async def on_feedback_fallback(cq: CallbackQuery):
    log.info("feedback fallback handled: %s", cq.data)
    try:
        await cq.answer("Принято!", show_alert=False)
        await cq.message.answer("Спасибо! 🙌")
    except Exception:
        pass
