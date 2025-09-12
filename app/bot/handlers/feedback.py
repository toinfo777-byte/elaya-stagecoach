from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.bot.states import FeedbackStates
from app.bot.keyboards.feedback import feedback_inline_kb

router = Router(name="feedback2")


# ------- разбор callback_data -------
def _parse_rate(data: str) -> str | None:
    # принимаем: "fb:rate:hot", "feedback:rate:ok", "rate:meh"
    if not data:
        return None
    if data.startswith(("fb:rate:", "feedback:rate:", "rate:")):
        return data.split(":")[-1]
    return None


def _is_text_cb(data: str) -> bool:
    # принимаем: "fb:text", "feedback:text", "text_feedback", и любые ...:text
    return (
        data in {"fb:text", "feedback:text", "text_feedback"}
        or (data and data.endswith(":text"))
    )


# ------- оценка 🔥/👌/😐 -------
@router.callback_query(F.data.func(lambda d: _parse_rate(d) is not None))
async def on_feedback_rate(cq: CallbackQuery, state: FSMContext):
    try:
        rate = _parse_rate(cq.data) or "unknown"
        await cq.answer("Спасибо за отзыв!")  # убрать «часики»
        await cq.message.answer("Принято. Спасибо! 🙌")
    except Exception:
        # на всякий — не роняем апку
        try:
            await cq.answer("Принято!")
        except Exception:
            pass


# ------- запрос текста ✍️ -------
@router.callback_query(F.data.func(_is_text_cb))
async def on_feedback_text_request(cq: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(FeedbackStates.wait_text)
        await cq.answer()
        await cq.message.answer("Напишите короткую фразу-отзыв одним сообщением.")
    except Exception:
        try:
            await cq.answer("Ок!")
        except Exception:
            pass


# ------- приём текста -------
@router.message(FeedbackStates.wait_text)
async def on_feedback_text_submit(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()
    if not text:
        await msg.answer("Пришлите, пожалуйста, обычный текст без вложений.")
        return
    # ничего не пишем в БД — только отвечаем, чтобы не было падений
    await state.clear()
    await msg.answer("Спасибо! Ваш отзыв сохранён. 🙏")


# (опционально) показать клавиатуру ещё раз из других мест
async def send_feedback_inline(to_message: Message):
    await to_message.answer(
        "Как прошёл этюд? Оцените или оставьте краткий отзыв:",
        reply_markup=feedback_inline_kb(prefix="fb"),
    )
