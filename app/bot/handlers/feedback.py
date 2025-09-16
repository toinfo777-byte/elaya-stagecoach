# app/bot/handlers/feedback.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message,
)

from app.bot.states import FeedbackStates  # wait_phrase

router = Router(name="feedback_v2")

# Нормализованные коды
FB_FIRE    = "fb_fire"
FB_OK      = "fb_ok"
FB_NEUTRAL = "fb_neutral"
FB_PHRASE  = "fb_phrase"

# Алиасы/префиксы — поддерживаем и старые клавиатуры
FIRE_PREFIXES    = (FB_FIRE,    "fire", "rate_fire", "rate_hot", "hot", "🔥")
OK_PREFIXES      = (FB_OK,      "ok",   "rate_ok",   "good",     "👌")
NEUTRAL_PREFIXES = (FB_NEUTRAL, "neutral", "meh", "so_so", "😐")
PHRASE_PREFIXES  = (FB_PHRASE,  "phrase", "text", "comment", "cmt", "1p", "fb_text")

def _starts_with_any(s: str, prefixes: tuple[str, ...]) -> bool:
    return any(s.startswith(p) for p in prefixes)

def make_feedback_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура отзывов: 🔥, 👌, 😐, затем «✍️ 1 фраза»."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔥", callback_data=FB_FIRE),
                InlineKeyboardButton(text="👌", callback_data=FB_OK),
                InlineKeyboardButton(text="😐", callback_data=FB_NEUTRAL),
            ],
            [InlineKeyboardButton(text="✍️ 1 фраза", callback_data=FB_PHRASE)],
        ]
    )

# ---------- ЭМОДЗИ-ОЦЕНКИ ----------
@router.callback_query(F.data.func(lambda d: _starts_with_any(d, FIRE_PREFIXES)))
async def on_fb_fire(cq: CallbackQuery) -> None:
    await cq.answer("🔥 Принял. Спасибо!", show_alert=False)

@router.callback_query(F.data.func(lambda d: _starts_with_any(d, OK_PREFIXES)))
async def on_fb_ok(cq: CallbackQuery) -> None:
    await cq.answer("👌 Принял. Спасибо!", show_alert=False)

@router.callback_query(F.data.func(lambda d: _starts_with_any(d, NEUTRAL_PREFIXES)))
async def on_fb_neutral(cq: CallbackQuery) -> None:
    await cq.answer("😐 Принял. Спасибо!", show_alert=False)

# ---------- «1 фраза» ----------
@router.callback_query(F.data.func(lambda d: _starts_with_any(d, PHRASE_PREFIXES)))
async def on_fb_phrase(cq: CallbackQuery, state: FSMContext) -> None:
    await cq.message.answer(
        "Напишите одну короткую фразу об этом этюде. Если передумали — отправьте /cancel."
    )
    await state.set_state(FeedbackStates.wait_phrase)
    await cq.answer()

@router.message(FeedbackStates.wait_phrase, ~F.text.startswith("/"))
async def on_fb_phrase_text(msg: Message, state: FSMContext) -> None:
    phrase = (msg.text or "").strip()
    if not phrase:
        await msg.answer("Нужна короткая фраза — одно предложение. Попробуем ещё раз?")
        return
    # TODO: при необходимости сохраните в БД/метрики
    await msg.answer("Супер, записал. Спасибо! 🎯")
    await state.clear()

@router.message(FeedbackStates.wait_phrase, Command("cancel"))
async def on_fb_phrase_cancel(msg: Message, state: FSMContext) -> None:
    await state.clear()
    await msg.answer("Ок, отменил ввод фразы.")

# ---------- Последний фолбэк в пространстве fb_* ----------
@router.callback_query(F.data.startswith("fb_"))
async def on_fb_namespace_fallback(cq: CallbackQuery) -> None:
    # Если сюда попали — значит формат неожиданный,
    # но лучше ответить «Принял», чтобы UX не ломать.
    await cq.answer("Принял 👍", show_alert=False)
