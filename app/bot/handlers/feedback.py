# app/bot/handlers/feedback.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.bot.states import FeedbackStates

router = Router(name="feedback2")

# ----- Клавиатура оценок -----
def feedback_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔥", callback_data="fb:hot"),
            InlineKeyboardButton(text="👌", callback_data="fb:ok"),
            InlineKeyboardButton(text="😐", callback_data="fb:meh"),
        ],
        [InlineKeyboardButton(text="✍ 1 фраза", callback_data="fb:text")],
    ])

# ----- Хелпер: показать «оценки» где угодно -----
async def prompt_feedback(message: Message, text: str = "Как прошёл этюд? Оцените или оставьте краткий отзыв:") -> None:
    await message.answer(text, reply_markup=feedback_kb())

# ====== HANDLERS ======

# Быстрые реакции
@router.callback_query(F.data.in_({"fb:hot", "fb:ok", "fb:meh"}))
async def on_quick_mark(cb: CallbackQuery):
    mark = {"fb:hot": "🔥", "fb:ok": "👌", "fb:meh": "😐"}[cb.data]
    # TODO: здесь можно записать оценку в БД/метрики
    await cb.answer("Спасибо!")
    # опционально — аккуратно обновить сообщение/написать новое
    # await cb.message.edit_reply_markup(reply_markup=None)

# Вход в режим «одна фраза»
@router.callback_query(F.data == "fb:text")
async def on_text_request(cb: CallbackQuery, state: FSMContext):
    await cb.answer()  # закрыть «окно»
    await cb.message.answer("Напишите короткий отзыв одной фразой. Чтобы отменить — /cancel")
    await state.set_state(FeedbackStates.wait_text)

# Приём одной фразы
@router.message(FeedbackStates.wait_text, F.text)
async def on_text_received(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()
    if not text or len(text) > 300:
        await msg.answer("Слишком длинно. Попробуйте одной короткой фразой (до 300 символов).")
        return

    # TODO: сохранить отзыв (user_id=msg.from_user.id, text=text)
    await state.clear()
    await msg.answer("Спасибо за отзыв! 🙌")
