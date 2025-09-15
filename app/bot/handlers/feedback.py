# app/bot/handlers/feedback.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.states import FeedbackStates

router = Router(name="feedback2")


# ==== публичный конструктор клавиатуры «оценок» ====
def feedback_keyboard():
    kb = InlineKeyboardBuilder()
    # три быстрые реакции
    kb.button(text="🔥", callback_data="fb:hot")
    kb.button(text="👌", callback_data="fb:ok")
    kb.button(text="😐", callback_data="fb:meh")
    # запрос фразы
    kb.button(text="✍ 1 фраза", callback_data="fb:phrase")
    kb.adjust(3, 1)
    return kb.as_markup()


# ==== обработчики быстрых реакций ====
@router.callback_query(F.data.in_({"fb:hot", "fb:ok", "fb:meh"}))
async def on_quick_reaction(cq: CallbackQuery):
    # здесь можно положить запись в БД/метрики
    # save_reaction(user_id=cq.from_user.id, reaction=cq.data[3:])
    # отвечаем, чтобы Telegram убрал «часики»
    try:
        await cq.answer("Ок")
    except Exception:
        pass


# ==== запуск режима «1 фраза» ====
@router.callback_query(F.data == "fb:phrase")
async def on_phrase_start(cq: CallbackQuery, state: FSMContext):
    await state.set_state(FeedbackStates.wait_phrase)
    try:
        await cq.answer()  # просто закрыть «часики»
    except Exception:
        pass

    await cq.message.answer(
        "Напишите одну короткую фразу об этом этюде. "
        "Если передумали — отправьте /cancel."
    )


# ==== приём фразы ====
@router.message(FeedbackStates.wait_phrase, F.text)
async def on_phrase_text(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()
    if not text:
        await msg.answer("Нужен текст одной фразой 🙂")
        return
    if len(text) > 200:
        await msg.answer("Слишком длинно. Пожалуйста, до 200 символов.")
        return

    # здесь можно сохранить в БД/метрики
    # save_phrase(user_id=msg.from_user.id, phrase=text)

    await state.clear()
    await msg.answer("Принял. Спасибо! 💙")


# ==== если прислали не-текст, когда ждём фразу ====
@router.message(FeedbackStates.wait_phrase)
async def on_phrase_wrong(msg: Message):
    await msg.answer("Жду короткий текст одной фразой. Либо /cancel.")
