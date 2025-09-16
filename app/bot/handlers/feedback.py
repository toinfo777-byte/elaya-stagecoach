# app/bot/handlers/feedback.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.routers.menu import main_menu

router = Router(name="feedback2")

EMOJI_FIRE = "🔥"
EMOJI_OK = "👌"
EMOJI_MEH = "😐"
BTN_PHRASE = "✍ 1 фраза"

class FeedbackStates(StatesGroup):
    wait_phrase = State()

# точные матчи по кнопкам-эмодзи
@router.message(StateFilter("*"), F.text == EMOJI_FIRE)
async def fb_fire(m: Message):
    await m.answer("🔥 Супер! Спасибо 🙌", reply_markup=main_menu())

@router.message(StateFilter("*"), F.text == EMOJI_OK)
async def fb_ok(m: Message):
    await m.answer("👌 Принял. Спасибо!", reply_markup=main_menu())

@router.message(StateFilter("*"), F.text == EMOJI_MEH)
async def fb_meh(m: Message):
    await m.answer("😐 Принял. Спасибо!", reply_markup=main_menu())

# переход в режим «короткая фраза»
@router.message(StateFilter("*"), F.text == BTN_PHRASE)
async def fb_phrase_start(m: Message, state: FSMContext):
    await state.set_state(FeedbackStates.wait_phrase)
    await m.answer("Напишите одну короткую фразу об этом этюде. Если передумали — отправьте /cancel.", reply_markup=main_menu())

# приём фразы
@router.message(FeedbackStates.wait_phrase, ~F.text.startswith("/"))
async def fb_phrase_save(m: Message, state: FSMContext):
    text = (m.text or "").strip()
    if not text:
        await m.answer("Напишите текстом одну короткую фразу, пожалуйста.", reply_markup=main_menu())
        return
    # здесь можете сохранить фразу в БД
    await state.clear()
    await m.answer("Спасибо! Принял ✍", reply_markup=main_menu())
