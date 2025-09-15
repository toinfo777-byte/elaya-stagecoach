# app/bot/handlers/feedback.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.states import FeedbackStates

router = Router(name="feedback2")


# ---------- ПУБЛИЧНАЯ ФУНКЦИЯ ----------
def feedback_keyboard():
    """
    Готовая инлайн-клавиатура с оценками:
    🔥 / 👌 / 😐 / ✍ 1 фраза

    Использование:
        await message.answer(
            "Как прошёл этюд? Оцените или оставьте краткий отзыв:",
            reply_markup=feedback_keyboard(),
        )
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="🔥", callback_data="fb:hot")
    kb.button(text="👌", callback_data="fb:ok")
    kb.button(text="😐", callback_data="fb:meh")
    kb.button(text="✍ 1 фраза", callback_data="fb:phrase")
    kb.adjust(3, 1)
    return kb.as_markup()


# ---------- БЫСТРЫЕ РЕАКЦИИ ----------
@router.callback_query(F.data.in_({"fb:hot", "fb:ok", "fb:meh"}))
async def on_quick_reaction(cq: CallbackQuery):
    # TODO: сохранить реакцию в БД/метрики по необходимости
    # save_reaction(user_id=cq.from_user.id, reaction=cq.data[3:])
    try:
        await cq.answer("Ок")   # закрыть «часики»
    except Exception:
        pass


# ---------- ЗАПРОС «1 ФРАЗА» ----------
@router.callback_query(F.data == "fb:phrase")
async def on_phrase_start(cq: CallbackQuery, state: FSMContext):
    await state.set_state(FeedbackStates.wait_phrase)
    try:
        await cq.answer()       # просто убрать «часики»
    except Exception:
        pass
    await cq.message.answer(
        "Напишите одну короткую фразу об этюде. "
        "Если передумали — отправьте /cancel."
    )


# ---------- ПРИЁМ ФРАЗЫ ----------
@router.message(FeedbackStates.wait_phrase, F.text)
async def on_phrase_text(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()
    if not text:
        await msg.answer("Нужен текст одной фразой 🙂")
        return
    if len(text) > 200:
        await msg.answer("Слишком длинно. До 200 символов, пожалуйста.")
        return

    # TODO: сохранить фразу
    # save_phrase(user_id=msg.from_user.id, phrase=text)

    await state.clear()
    await msg.answer("Принял. Спасибо! 💙")


# ---------- НЕ-ТЕКСТ ВО ВРЕМЯ ОЖИДАНИЯ ----------
@router.message(FeedbackStates.wait_phrase)
async def on_phrase_wrong(msg: Message):
    await msg.answer("Жду короткий текст одной фразой. Либо /cancel.")
