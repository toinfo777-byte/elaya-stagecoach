# app/bot/handlers/feedback.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

from app.bot.states import FeedbackStates

router = Router(name="feedback2")

# ---------- КЛАВИАТУРА ОЦЕНОК ----------
def make_feedback_kb() -> "InlineKeyboardMarkup":
    kb = InlineKeyboardBuilder()
    kb.button(text="🔥", callback_data="fb:rate:fire")
    kb.button(text="👌", callback_data="fb:rate:ok")
    kb.button(text="😐", callback_data="fb:rate:meh")
    kb.adjust(3)

    kb.button(text="✍ 1 фраза", callback_data="fb:phrase")
    kb.adjust(3, 1)
    return kb.as_markup()

# ---------- HANDLERS: ОЦЕНКА ----------
@router.callback_query(F.data.startswith("fb:rate:"))
async def on_rate(cb: CallbackQuery):
    # здесь можно записать метрику/в БД
    # пример: kind = cb.data.split(":")[2]  # fire|ok|meh
    try:
        await cb.answer("Спасибо! Принял 👍", show_alert=False)
    except Exception:
        # если что-то не так — просто молча отвечаем
        await cb.answer()

# ---------- HANDLERS: ЗАПРОС ФРАЗЫ ----------
@router.callback_query(F.data == "fb:phrase")
async def on_phrase_request(cb: CallbackQuery, state):
    # переводим в состояние «ждём фразу»
    await state.set_state(FeedbackStates.wait_phrase)
    await cb.answer()  # убираем "часики"
    await cb.message.answer(
        "Напишите короткую фразу-отзыв одним сообщением.\n"
        "Можно отменить командой /cancel."
    )

# Пришёл текст в состоянии ожидания — сохраняем
@router.message(FeedbackStates.wait_phrase, F.text)
async def on_phrase_text(msg: Message, state):
    text = (msg.text or "").strip()
    if len(text) < 2:
        await msg.answer("Слишком коротко. Напишите пару слов, пожалуйста.")
        return
    if len(text) > 400:
        await msg.answer("Очень длинно. Укоротите до 400 символов 🙏")
        return

    # TODO: сохраните в вашу БД/метрики при необходимости
    # save_feedback_phrase(user_id=msg.from_user.id, phrase=text)

    await state.clear()
    await msg.answer("Сохранил! Спасибо за фидбек ✨")

# Любой нетекст в состоянии — просим текст
@router.message(FeedbackStates.wait_phrase)
async def on_phrase_non_text(msg: Message):
    await msg.answer("Нужен именно текст одним сообщением. Или /cancel.")

# ---------- ДЕМО-КОМАНДА ДЛЯ ПРОВЕРКИ ----------
@router.message(Command("feedback_demo"))
async def feedback_demo(msg: Message):
    await msg.answer(
        "Как прошёл этюд? Оцените или оставьте короткий отзыв:",
        reply_markup=make_feedback_kb(),
    )
