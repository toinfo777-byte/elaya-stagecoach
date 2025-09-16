from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.routers.menu import main_menu

router = Router(name="feedback")

# На случай разных вариантов callback_data в старом/новом коде:
EMOJI_DATAS = {
    "🔥", "👌", "😐",
    "fire", "ok", "meh", "like", "neutral", "dislike", "hot",
    "fb_fire", "fb_ok", "fb_meh",
}

PHRASE_DATAS = {"phrase", "fb_phrase", "fb:phrase", "✍️ 1 фраза"}

class OnePhrase(StatesGroup):
    awaiting = State()

# ——— Эмодзи-оценки ———
@router.callback_query(F.data.in_(EMOJI_DATAS))
async def feedback_emoji(cq: CallbackQuery):
    # короткий pop-up, чтобы не зашумлять чат
    await cq.answer("Принял. Спасибо! 👍", show_alert=False)

# ——— «1 фраза» ———
@router.callback_query(F.data.in_(PHRASE_DATAS))
async def feedback_phrase_start(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await cq.message.answer(
        "Напишите одну короткую фразу об этом этюде. Если передумали — отправьте /cancel.",
        reply_markup=main_menu()
    )
    await state.set_state(OnePhrase.awaiting)

@router.message(OnePhrase.awaiting, ~F.text.startswith("/"))
async def feedback_phrase_save(m: Message, state: FSMContext):
    # здесь можно сохранить фразу в базу
    await state.clear()
    await m.answer("Спасибо! Сохранил ✍️", reply_markup=main_menu())

@router.message(OnePhrase.awaiting, F.text == "/cancel")
async def feedback_phrase_cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Ок, без фразы. Возвращаю в меню.", reply_markup=main_menu())
