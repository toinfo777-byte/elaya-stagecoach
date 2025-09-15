# app/bot/handlers/feedback.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.bot.states import FeedbackStates

router = Router(name="feedback2_router")

# =========================
# Клавиатуры
# =========================

def build_feedback_kb() -> InlineKeyboardMarkup:
    """
    🔥 / 👌 / 😐  +  ✍ 1 фраза
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔥", callback_data="fb:rate:hot"),
            InlineKeyboardButton(text="👌", callback_data="fb:rate:ok"),
            InlineKeyboardButton(text="😐", callback_data="fb:rate:meh"),
        ],
        [InlineKeyboardButton(text="✍ 1 фраза", callback_data="fb:phrase")],
    ])

async def send_feedback_keyboard(message: Message) -> None:
    """
    Показать универсальную клавиатуру отзывов рядом с любым сообщением.
    Вызывайте из тренировки/любого места:
        await send_feedback_keyboard(message)
    """
    await message.answer(
        "Как прошёл этюд? Оцените или оставьте короткий отзыв:",
        reply_markup=build_feedback_kb(),
    )

# =========================
# Хендлеры рейтинга
# =========================

@router.callback_query(F.data.startswith("fb:rate:"))
async def on_feedback_rate(call: CallbackQuery):
    # Здесь можете положить в БД/метрики, по желанию
    # value = call.data.split(":")[-1]  # hot/ok/meh
    await call.answer("Спасибо! Принял 👍", show_alert=False)

    # Ничего «не поднимаем», просто выходим — этого достаточно,
    # чтобы другие хендлеры не мешали (у нас узкий фильтр F.data.startswith).


# =========================
# Хендлер «1 фраза»
# =========================

@router.callback_query(F.data == "fb:phrase")
async def feedback_phrase_start(call: CallbackQuery, state: FSMContext):
    # Входим в состояние ожидания фразы
    await state.set_state(FeedbackStates.wait_phrase)
    await call.message.answer(
        "Напишите одну короткую фразу об этом этюде. Если передумали — отправьте /cancel."
    )
    await call.answer()  # закрыть «часики»


@router.message(FeedbackStates.wait_phrase, F.text)
async def feedback_phrase_take(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()
    if not text:
        await msg.answer("Пусто 🙈 Напишите короткую фразу или /cancel.")
        return

    # Здесь сохраните куда нужно (БД/метрики)
    # save_short_feedback(user_id=msg.from_user.id, text=text)

    await state.clear()
    await msg.answer("Принял! Спасибо 🙌")


# =========================
# Отмена ожидания фразы
# =========================

@router.message(FeedbackStates.wait_phrase, F.text.in_({"/cancel", "cancel"}))
async def feedback_phrase_cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Окей, отменил. Можете продолжать. /menu")
