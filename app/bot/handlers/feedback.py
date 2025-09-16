# app/bot/handlers/feedback.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from app.bot.states import FeedbackStates

# Сабджектные кнопки (ровно те, что рисуешь в тренировке)
EMOJI_HOT = "🔥"
EMOJI_OK = "👌"
EMOJI_MEH = "😐"
BTN_PHRASE = "✍️ 1 фраза"

router = Router(name="feedback2")

# ---- реакции на эмодзи (в любом состоянии) ----
@router.message(StateFilter("*"), F.text == EMOJI_HOT)
async def fb_hot(m: Message):
    await m.answer("🔥 Супер! Принял, спасибо!")

@router.message(StateFilter("*"), F.text == EMOJI_OK)
async def fb_ok(m: Message):
    await m.answer("👌 Отлично! Принял, спасибо!")

@router.message(StateFilter("*"), F.text == EMOJI_MEH)
async def fb_meh(m: Message):
    await m.answer("😐 Понял. Принято!")

# ---- «1 фраза» → ждём текст ----
@router.message(StateFilter("*"), F.text == BTN_PHRASE)
async def fb_phrase_start(m: Message, state: FSMContext):
    await state.set_state(FeedbackStates.wait_phrase)
    await m.answer("Напишите одну короткую фразу об этом этюде. Если передумали — отправьте /cancel.")

@router.message(FeedbackStates.wait_phrase, ~F.text.startswith("/"))
async def fb_phrase_save(m: Message, state: FSMContext):
    # Здесь можешь записать в БД — я просто подтверждаю
    phrase = (m.text or "").strip()
    if not phrase:
        await m.answer("Фраза пустая — напишите коротко что заметили или /cancel.")
        return
    await state.clear()
    await m.answer("Спасибо! Принял ✍️")
