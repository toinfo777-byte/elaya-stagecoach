# app/routers/feedback.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router(name="feedback2")

# состояние для «✍ 1 фраза»
class FeedbackStates(StatesGroup):
    wait_phrase = State()

# ==== клавиатура отзывов ====
def kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔥", callback_data="fb:fire"),
            InlineKeyboardButton(text="👌", callback_data="fb:ok"),
            InlineKeyboardButton(text="😐", callback_data="fb:meh"),
        ],
        [InlineKeyboardButton(text="✍ 1 фраза", callback_data="fb:phrase")],
    ])

# ==== обработчики ====
@router.callback_query(F.data.startswith("fb:"))
async def on_feedback_buttons(cq: CallbackQuery, state: FSMContext):
    action = cq.data.split(":", 1)[1]
    if action == "phrase":
        await state.set_state(FeedbackStates.wait_phrase)
        await cq.message.answer("Напишите одну короткую фразу об этом этюде. Если передумали — отправьте /cancel.")
        await cq.answer()
        return

    # простая фиксация реакции (при желании добавь запись в БД)
    txt = {"fire": "🔥 Огонь!", "ok": "👌 Принято!", "meh": "😐 Ок"}[action]
    await cq.answer("Спасибо! Принял 👍", show_alert=False)
    # Можно ответом в чат (по желанию):
    # await cq.message.answer(txt)

@router.message(FeedbackStates.wait_phrase, F.text)
async def on_feedback_phrase(msg: Message, state: FSMContext):
    phrase = (msg.text or "").strip()
    if not phrase:
        await msg.answer("Одной короткой фразой, пожалуйста 🙂")
        return

    # здесь можно сохранить в БД
    # save_phrase(user_id=msg.from_user.id, phrase=phrase)

    await state.clear()
    await msg.answer("Готово! Сохранил 👍")

# если в режиме ожидания фразы прилетит команда — выходим
@router.message(FeedbackStates.wait_phrase, F.text.startswith("/"))
async def on_feedback_phrase_cmd(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Отменил. Возвращаюсь.")
