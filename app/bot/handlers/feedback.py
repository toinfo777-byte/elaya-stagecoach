# app/bot/handlers/feedback.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

router = Router(name="feedback2")

# ==== состояние «жду короткую фразу» ====
class FeedbackS(StatesGroup):
    wait_text = State()

# ==== клавиатура «оценок» (🔥/👌/😐 + ✍ 1 фраза) ====
def feedback_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔥", callback_data="fb:rate:fire"),
            InlineKeyboardButton(text="👌", callback_data="fb:rate:ok"),
            InlineKeyboardButton(text="😐", callback_data="fb:rate:meh"),
        ],
        [InlineKeyboardButton(text="✍ 1 фраза", callback_data="fb:text")],
    ])

# ВЫЗЫВАТЬ ОТКУДА УГОДНО:
# await send_feedback_block(message)  или await send_feedback_block(callback.message)
async def send_feedback_block(target: Message) -> None:
    await target.answer(
        "Как прошёл этюд? Оцените или оставьте краткий отзыв:",
        reply_markup=feedback_kb(),
    )

# ==== обработчики кнопок «оценок» ====

@router.callback_query(F.data.startswith("fb:rate:"))
async def on_rate(cb: CallbackQuery, state: FSMContext):
    rate = cb.data.split(":")[-1]  # fire / ok / meh
    # TODO: здесь сохраните рейтинг в БД/метрики при необходимости
    # save_rating(user_id=cb.from_user.id, value=rate)

    await cb.answer("Принято ✅")
    await cb.message.answer(
        "Спасибо! Если хотите — напишите короткую фразу о впечатлении.",
        reply_markup=feedback_kb(),   # можно повторно показать блок
    )

@router.callback_query(F.data == "fb:text")
async def on_text_request(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(FeedbackS.wait_text)
    await cb.message.answer("Напишите 1 короткую фразу (до 200 символов).")

@router.message(FeedbackS.wait_text, F.text)
async def on_text_received(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()
    if not text or len(text) > 200:
        await msg.answer("Пожалуйста, 1 короткую фразу (до 200 символов).")
        return

    # TODO: сохраните фразу куда нужно
    # save_feedback_text(user_id=msg.from_user.id, text=text)

    # ВАЖНО: выходим из состояния, но данные FSM не чистим насильно
    await state.set_state(None)
    await msg.answer("Готово! Сохранил 👍")

# На случай, если пользователь прислал что-то не текстом
@router.message(FeedbackS.wait_text)
async def on_text_required(msg: Message):
    await msg.answer("Жду короткую текстовую фразу 🙂")
