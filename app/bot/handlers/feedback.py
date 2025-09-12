# app/bot/handlers/feedback.py
from __future__ import annotations

from aiogram import Router, F, html
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.utils.tg_safe import safe_answer, safe_edit_text, safe_edit_reply_markup

import logging
log = logging.getLogger(__name__)

router = Router(name="feedback2")


# ---------- ВСПОМОГАТЕЛЬНОЕ ----------

class FB(StatesGroup):
    waiting_phrase = State()


def _kb_feedback() -> InlineKeyboardMarkup:
    # 🔥/👌/😐 + «1 фраза»
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔥", callback_data="fb:rate:hot"),
            InlineKeyboardButton(text="👌", callback_data="fb:rate:ok"),
            InlineKeyboardButton(text="😐", callback_data="fb:rate:meh"),
        ],
        [InlineKeyboardButton(text="✍ 1 фраза", callback_data="fb:phrase")],
    ])


async def ask_short_review(msg: Message) -> None:
    await msg.answer(
        "Как прошёл этюд? Оцените или оставьте краткий отзыв:",
        reply_markup=_kb_feedback(),
    )


# ---------- ХЭНДЛЕРЫ КОЛЛБЭКОВ ----------

@router.callback_query(F.data.startswith("fb:rate:"))
async def on_feedback_rate(cb: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатываем оценку по кнопке 🔥/👌/😐
    """
    rate = cb.data.split(":", 2)[-1]  # hot | ok | meh
    await safe_answer(cb)  # игнорируем возможный 'query is too old'

    # лог + здесь можно записать в БД/метрику
    try:
        user_id = cb.from_user.id if cb.from_user else None
        log.info("FEEDBACK RATE: user=%s rate=%s", user_id, rate)
        # TODO: тут сохранение в БД/метрики (если нужно)
    except Exception as e:
        log.exception("save rate failed: %s", e)

    # Пытаемся отредактировать исходное сообщение,
    # если нельзя — просто шлём новое.
    txt = f"Спасибо! Оценка: {html.bold(rate)} записана."
    edited = await safe_edit_text(cb.message, txt)
    if edited is None:
        await cb.message.answer(txt)


@router.callback_query(F.data == "fb:phrase")
async def on_feedback_phrase_start(cb: CallbackQuery, state: FSMContext) -> None:
    """
    Просим короткую фразу-отзыв и ставим стейт.
    """
    await safe_answer(cb)

    prompt = "Введите краткую фразу-отзыв одним сообщением:"
    edited = await safe_edit_text(cb.message, prompt)
    if edited is None:
        await cb.message.answer(prompt)

    await state.set_state(FB.waiting_phrase)


# ---------- ХЭНДЛЕР ВВОДА ФРАЗЫ ----------

@router.message(FB.waiting_phrase)
async def on_feedback_phrase_text(msg: Message, state: FSMContext) -> None:
    phrase = (msg.text or "").strip()

    # лог + сохранить в БД/метрику при необходимости
    try:
        log.info("FEEDBACK PHRASE: user=%s phrase=%r", msg.from_user.id, phrase)
        # TODO: тут сохранение фразы
    except Exception as e:
        log.exception("save phrase failed: %s", e)

    await msg.answer("Спасибо! Отзыв записан 🙏")
    await state.clear()

    # Предложим снова стандартные кнопки для удобства
    await ask_short_review(msg)
