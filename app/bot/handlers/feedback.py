# app/bot/handlers/feedback.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router(name="feedback2")

# --- Состояние для ввода одной фразы
class FeedbackStates(StatesGroup):
    wait_phrase = State()


# --- Универсальная клавиатура оценок (можно вызывать где угодно)
def build_feedback_kb() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="🔥", callback_data="fb_rate:hot"),
            InlineKeyboardButton(text="👌", callback_data="fb_rate:ok"),
            InlineKeyboardButton(text="😐", callback_data="fb_rate:meh"),
        ],
        [InlineKeyboardButton(text="✍ 1 фраза", callback_data="fb_phrase:start")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# --- «Показать оценки» по командам /feedback или /rate
@router.message(F.text.in_({"/feedback", "/rate"}))
async def show_feedback_keyboard(msg: Message):
    await msg.answer("Как прошёл этюд? Оцените или оставьте короткий отзыв:", reply_markup=build_feedback_kb())


# --- Нормализуем любые алиасы коллбэков, чтобы ловить старые/разные варианты
_RATE_ALIASES = {
    "hot": {"fb_rate:hot", "fb:hot", "feedback:hot", "rate:hot", "r:hot"},
    "ok":  {"fb_rate:ok",  "fb:ok",  "feedback:ok",  "rate:ok",  "r:ok"},
    "meh": {"fb_rate:meh", "fb:meh", "feedback:meh", "rate:meh", "r:meh"},
}
_ALL_RATE_TOKENS = set().union(*_RATE_ALIASES.values())

_PHRASE_ALIASES = {"fb_phrase:start", "fb:phrase", "feedback:phrase", "rate:phrase", "r:phrase"}


def _canon_rate(token: str) -> str | None:
    for key, bag in _RATE_ALIASES.items():
        if token in bag:
            return key
    return None


# --- Обработка оценок 🔥/👌/😐
@router.callback_query(F.data.in_(_ALL_RATE_TOKENS))
async def handle_rate(call: CallbackQuery):
    rate = _canon_rate(call.data)
    # ACK, чтобы исчез «крутится…»
    await call.answer()
    # Здесь можно записать в БД/метрики:
    # save_rating(user_id=call.from_user.id, rate=rate)

    # Аккуратно «фиксируем» сообщение: уберём клавиатуру, чтобы не спамили кликами
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    emoji = {"hot": "🔥", "ok": "👌", "meh": "😐"}[rate or "ok"]
    await call.message.answer(f"Спасибо за отметку {emoji}! Учтено.")


# --- Кнопка «✍ 1 фраза» — просим текст
@router.callback_query(F.data.in_(_PHRASE_ALIASES))
async def ask_one_phrase(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(FeedbackStates.wait_phrase)
    await call.message.answer(
        "Напишите одну короткую фразу — чем был полезен этюд/шаг.\n"
        "Если передумали — /cancel"
    )


# --- Принимаем саму «1 фразу»
@router.message(FeedbackStates.wait_phrase, F.text)
async def save_one_phrase(msg: Message, state: FSMContext):
    phrase = (msg.text or "").strip()
    if not phrase or len(phrase) > 300:
        await msg.answer("Одной-двумя короткими фразами, пожалуйста 🙂")
        return

    # Сохраняем куда нужно
    # save_phrase(user_id=msg.from_user.id, phrase=phrase)

    await state.clear()
    await msg.answer("Принято, спасибо! ✍️")
