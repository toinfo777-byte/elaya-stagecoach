# app/bot/handlers/feedback.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from app.bot.states import FeedbackStates
from app.bot.keyboards.feedback import feedback_inline_kb
from app.storage.repo import session_scope, log_event

router = Router()
router.name = "feedback2"

# Простая клавиатура «В меню» — шлёт /cancel (у тебя это открывает меню)
def menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="/cancel")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

# 1) Поймать клик на оценку (🔥/👌/😐)
@router.callback_query(F.data.startswith("fb:rate:"))
async def on_feedback_rate(cb: CallbackQuery, state: FSMContext):
    # fb:rate:hot | ok | meh
    try:
        _, _, rate = (cb.data or "").split(":", 2)
    except Exception:
        rate = "unknown"

    # логируем событие (не ломаем основной поток)
    try:
        with session_scope() as s:
            uid = cb.from_user.id if cb.from_user else None
            log_event(s, user_id=uid, name="feedback_rate", payload={"rate": rate})
    except Exception:
        pass

    await cb.answer("Спасибо за отклик!")
    await cb.message.answer(
        "Хочешь добавить короткий комментарий? Напиши 1 фразу и я сохраню.\n"
        "Или нажми /cancel чтобы вернуться в меню.",
        reply_markup=menu_kb(),
    )
    await state.set_state(FeedbackStates.wait_text)


# 2) Кнопка «✍️ 1 фраза»
@router.callback_query(F.data == "fb:phrase")
async def on_feedback_phrase(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await cb.message.answer(
        "Напиши, пожалуйста, 1 фразу — что было ценного/что улучшить.",
        reply_markup=menu_kb(),
    )
    await state.set_state(FeedbackStates.wait_text)


# 3) Пришёл текст «1 фраза»
@router.message(FeedbackStates.wait_text, F.text.len() > 0)
async def save_feedback_text(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()
    try:
        with session_scope() as s:
            uid = msg.from_user.id if msg.from_user else None
            log_event(s, user_id=uid, name="feedback_text", payload={"text": text})
    except Exception:
        pass

    await msg.answer("Сохранил. Спасибо! 🙌", reply_markup=None)
    await state.clear()
