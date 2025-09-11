# app/bot/handlers/feedback.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from app.bot.states import FeedbackStates
from app.bot.keyboards.feedback import feedback_inline_kb  # твоя инлайн-клава c 🔥/👌/😐 и "1 фраза"
from app.storage.repo import session_scope, log_event

router = Router(name="feedback2")

# Простая клавиатура "в меню" — шлёт /cancel (у тебя это открывает меню)
def menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="/cancel")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

# ----- 1) Поймать клик на оценку 🔥/👌/😐 -----
@router.callback_query(F.data.startswith("fb:rate:"))
async def on_feedback_rate(cb: CallbackQuery, state: FSMContext):
    # fb:rate:hot | ok | meh
    _, _, rate = cb.data.split(":", 2)
    await state.update_data(rate=rate)

    # просим одно предложение
    await cb.message.answer(
        "Принято 👍\nНапиши, пожалуйста, одну фразу: что именно получилось/не получилось?",
        reply_markup=menu_kb(),
    )
    await cb.answer()  # закрыть "часики"
    await state.set_state(FeedbackStates.wait_text)

# ----- 2) Пользователь выбрал «1 фраза» из инлайн-клавы без оценки -----
@router.callback_query(F.data == "fb:text")
async def on_feedback_text_only(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer(
        "Окей, напиши коротко одной фразой 🙏",
        reply_markup=menu_kb(),
    )
    await cb.answer()
    await state.set_state(FeedbackStates.wait_text)

# ----- 3) Принять свободный текст и сохранить -----
@router.message(FeedbackStates.wait_text)
async def on_feedback_text(msg: Message, state: FSMContext):
    data = await state.get_data()
    rate = data.get("rate")  # может быть None, если человек нажал сразу «1 фраза»

    payload = {
        "tg_id": msg.from_user.id,
        "username": msg.from_user.username,
        "rate": rate,                # "hot" | "ok" | "meh" | None
        "text": msg.text.strip(),
        "message_id": msg.message_id,
    }

    # Логируем безопасно (user_id нам неизвестен — кладём None и tg_id в payload)
    try:
        with session_scope() as s:
            log_event(s, user_id=None, name="feedback_added", payload=payload)
    except Exception:
        # не роняем поток, спасибо и так отправим
        pass

    await state.clear()
    await msg.answer(
        "Спасибо! Сохранил отзыв 🙌\nНажми /cancel, чтобы вернуться в меню.",
        reply_markup=menu_kb(),
    )

# ----- 4) Запасной вход: показать инлайн-клаву с оценками -----
@router.message(F.text.casefold() == "отзыв")
async def show_feedback_buttons(msg: Message):
    await msg.answer(
        "Как прошёл этюд? Оцени или оставь краткий отзыв:",
        reply_markup=feedback_inline_kb(),
    )
