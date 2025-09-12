# app/bot/handlers/feedback.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.bot.states import FeedbackStates
from app.bot.keyboards.feedback import feedback_inline_kb
from app.storage.repo import session_scope, log_event

router = Router(name="feedback2")


# ---- 1) Оценка эмодзи: 🔥/👌/😐 -------------------------------------------
@router.callback_query(F.data.startswith("fb:rate:"))
async def on_feedback_rate(cq: CallbackQuery, state: FSMContext):
    # data: "fb:rate:hot|ok|meh"
    try:
        _, _, rate = cq.data.split(":", 2)
    except Exception:
        await cq.answer("Что-то пошло не так…", show_alert=False)
        return

    # логируем событие
    with session_scope() as s:
        tg_id = cq.from_user.id
        # у вас есть user_id? Если нужно — найдёте по tg_id в логере
        log_event(s, user_id=None, name="feedback_added", payload={"kind": rate, "src": "inline"})

    # быстрый ответ на клик, чтобы “часики” исчезли
    await cq.answer("Спасибо за отзыв!", show_alert=False)

    # можно мягко подтвердить сообщением (не меняя вашу разметку)
    await cq.message.answer("Принято. Спасибо! 🙌")


# ---- 2) Запрос “1 фраза” ---------------------------------------------------
@router.callback_query(F.data == "fb:text")
async def on_feedback_text_request(cq: CallbackQuery, state: FSMContext):
    await state.set_state(FeedbackStates.wait_text)
    await cq.answer()  # снимаем "часики"
    await cq.message.answer("Напишите короткую фразу-отзыв одним сообщением.")


# ---- 3) Приём текста в состоянии wait_text ---------------------------------
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


# ---- 4) (опционально) показать клавиатуру ещё раз --------------------------
# Если где-то нужно пересоздать инлайн-клаву:
async def send_feedback_inline(to_message: Message):
    await to_message.answer(
        "Как прошёл этюд? Оцените или оставьте краткий отзыв:",
        reply_markup=feedback_inline_kb(prefix="fb"),
    )
