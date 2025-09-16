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

# --- нормализованные коды
FB_FIRE    = "fb_fire"
FB_OK      = "fb_ok"
FB_NEUTRAL = "fb_neutral"
FB_PHRASE  = "fb_phrase"

# --- алиасы на случай старых клавиатур
FIRE_ALIASES    = {FB_FIRE, "fire", "rate_fire", "rate_hot", "hot", "🔥"}
OK_ALIASES      = {FB_OK, "ok", "rate_ok", "good", "👌"}
NEUTRAL_ALIASES = {FB_NEUTRAL, "neutral", "meh", "so_so", "😐"}
PHRASE_ALIASES  = {FB_PHRASE, "phrase", "text", "comment", "cmt", "1p", "fb_text"}

def make_feedback_keyboard() -> InlineKeyboardMarkup:
    """Единая клавиатура отзывов (правильный порядок: 🔥, 👌, 😐, затем «✍️ 1 фраза»)."""
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
@router.callback_query(F.data.func(lambda d: d in FIRE_ALIASES))
async def on_fb_fire(cq: CallbackQuery) -> None:
    await cq.answer("🔥 Принял. Спасибо!", show_alert=False)

@router.callback_query(F.data.func(lambda d: d in OK_ALIASES))
async def on_fb_ok(cq: CallbackQuery) -> None:
    await cq.answer("👌 Принял. Спасибо!", show_alert=False)

@router.callback_query(F.data.func(lambda d: d in NEUTRAL_ALIASES))
async def on_fb_neutral(cq: CallbackQuery) -> None:
    await cq.answer("😐 Принял. Спасибо!", show_alert=False)

# ---------- «1 фраза» ----------
@router.callback_query(F.data.func(lambda d: d in PHRASE_ALIASES))
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
    # TODO: здесь можно сохранить фразу в БД/метрики
    await msg.answer("Супер, записал. Спасибо! 🎯")
    await state.clear()

@router.message(FeedbackStates.wait_phrase, Command("cancel"))
async def on_fb_phrase_cancel(msg: Message, state: FSMContext) -> None:
    await state.clear()
    await msg.answer("Ок, отменил ввод фразы.")

# ---------- подстраховка: если прилетело fb_* но ни один из хэндлеров не совпал ----------
@router.callback_query(F.data.startswith("fb_"))
async def on_fb_namespace_fallback(cq: CallbackQuery) -> None:
    # попали сюда — значит callback_data нестандартная, но из нашего пространства имён
    await cq.answer("Принял 👍", show_alert=False)
