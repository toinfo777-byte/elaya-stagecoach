from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.bot.states import FeedbackStates
from app.bot.keyboards.feedback import feedback_inline_kb
from app.storage.repo import session_scope, log_event

router = Router(name="feedback2")


# утилита: понять тип колбэка и значение
def _parse_rate(data: str) -> str | None:
    # принимает: "fb:rate:hot", "feedback:rate:ok", "rate:meh"
    if not data:
        return None
    if data.startswith(("fb:rate:", "feedback:rate:", "rate:")):
        return data.split(":")[-1]  # hot|ok|meh
    return None


def _is_text_cb(data: str) -> bool:
    # принимает: "fb:text", "feedback:text", "text_feedback", "rate:text" (на всякий на будущее)
    return (
        data in {"fb:text", "feedback:text", "text_feedback"}
        or data.endswith(":text")
    )


# ---- 1) клик на оценку 🔥/👌/😐 ---------------------------------------------
@router.callback_query(F.data.func(lambda d: _parse_rate(d) is not None))
async def on_feedback_rate(cq: CallbackQuery, state: FSMContext):
    rate = _parse_rate(cq.data)
    if not rate:
        await cq.answer("Что-то пошло не так…")
        return

    with session_scope() as s:
        log_event(s, user_id=None, name="feedback_added", payload={"kind": rate, "src": "inline"})

    await cq.answer("Спасибо за отзыв!")          # снять «часики»
    await cq.message.answer("Принято. Спасибо! 🙌")


# ---- 2) запрос текста ✍️ ---------------------------------------------------
@router.callback_query(F.data.func(_is_text_cb))
async def on_feedback_text_request(cq: CallbackQuery, state: FSMContext):
    await state.set_state(FeedbackStates.wait_text)
    await cq.answer()
    await cq.message.answer("Напишите короткую фразу-отзыв одним сообщением.")


# ---- 3) приём текста --------------------------------------------------------
@router.message(FeedbackStates.wait_text)
async def on_feedback_text_submit(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()
    if not text:
        await msg.answer("Пришлите, пожалуйста, обычный текст без вложений.")
        return

    with session_scope() as s:
        log_event(s, user_id=None, name="feedback_added", payload={"kind": "text", "text": text})

    await state.clear()
    await msg.answer("Спасибо! Ваш отзыв сохранён. 🙏")


# ---- 4) хелпер для показа клавы ещё раз (если нужно где-то вызвать) --------
async def send_feedback_inline(to_message: Message):
    await to_message.answer(
        "Как прошёл этюд? Оцените или оставьте краткий отзыв:",
        reply_markup=feedback_inline_kb(prefix="fb"),
    )
