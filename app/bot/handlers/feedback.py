# app/bot/handlers/feedback.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.states import FeedbackStates
from app.routers.menu import main_menu

router = Router(name="feedback2")

# ===== Вспомогалки =====
PHRASE_BUTTON_TEXT = "✍ 1 фраза"

PROMPT_TEXT = (
    "Напишите одну короткую фразу об этом этюде. "
    "Если передумали — отправьте /cancel."
)

OK_SAVED = "Спасибо! Принял 📝"

def _is_short_phrase(text: str) -> bool:
    t = (text or "").strip()
    return 3 <= len(t) <= 120 and not t.startswith("/")

# ===== РЕЙТИНГИ (🔥/👌/😐) — принимаем колбэки любых наших клавиатур =====
@router.callback_query(F.data.in_({"fb:rate:hot", "fb:rate:ok", "fb:rate:meh"}))
async def fb_rate_any(cq: CallbackQuery):
    # здесь можно положить в БД/метрики по желанию
    # save_rating(user_id=cq.from_user.id, value=...)
    try:
        await cq.answer("Спасибо! Принял 👍", show_alert=False)
    except Exception:
        # на всякий случай, если уже отвечали — молча игнорируем
        pass

# ===== ЗАПРОС ФРАЗЫ =====
# 1) Inline-кнопка «фраза» (callback)
@router.callback_query(F.data == "fb:phrase")
async def fb_phrase_inline(cq: CallbackQuery, state: FSMContext):
    await state.set_state(FeedbackStates.wait_phrase)
    await cq.message.answer(PROMPT_TEXT)
    try:
        await cq.answer()  # закрыть "часики"
    except Exception:
        pass

# 2) На случай текстовой кнопки/шортката «✍ 1 фраза»
@router.message(StateFilter("*"), F.text == PHRASE_BUTTON_TEXT)
async def fb_phrase_text_btn(msg: Message, state: FSMContext):
    await state.set_state(FeedbackStates.wait_phrase)
    await msg.answer(PROMPT_TEXT)

# 3) Разрешить отмену во время ожидания
@router.message(FeedbackStates.wait_phrase, Command("cancel"))
async def fb_phrase_cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Ок, не сохраняю. Возвращаю в меню.", reply_markup=main_menu())

# 4) Принимаем саму фразу
@router.message(FeedbackStates.wait_phrase, F.text)
async def fb_phrase_save(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()
    if not _is_short_phrase(text):
        await msg.answer("Коротко, пожалуйста (3–120 символов). Или /cancel.")
        return

    # TODO: тут ваш апдейт в БД/метрики
    # save_phrase(user_id=msg.from_user.id, phrase=text)

    await state.clear()
    await msg.answer(OK_SAVED, reply_markup=main_menu())

# 5) Любые другие типы сообщений в этом состоянии
@router.message(FeedbackStates.wait_phrase)
async def fb_phrase_other(msg: Message):
    await msg.answer("Жду короткую фразу текстом. Или /cancel.")
