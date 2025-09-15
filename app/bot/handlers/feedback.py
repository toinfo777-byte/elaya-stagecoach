# app/bot/handlers/feedback.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.states import FeedbackStates
from app.routers.menu import main_menu

router = Router(name="feedback2")

# ===== Константы =====
PHRASE_BUTTON_TEXT = "✍ 1 фраза"
PROMPT_TEXT = (
    "Напишите одну короткую фразу об этом этюде. "
    "Если передумали — отправьте /cancel."
)
OK_SAVED = "Спасибо! Принял 📝"

def _is_short_phrase(text: str) -> bool:
    t = (text or "").strip()
    return 3 <= len(t) <= 120 and not t.startswith("/")

# ===== Оценки (🔥/👌/😐) — ловим максимально широко =====
def _is_rate_cb(data: str | None) -> bool:
    if not data:
        return False
    d = data.lower()
    # совпадем и с "fb:rate:hot", и с "rate:ok", и с "training:rate:meh", и т.п.
    if "rate" in d and any(k in d for k in ("hot", "ok", "meh", "good", "bad", "1", "2", "3")):
        return True
    return False

@router.callback_query(F.data.func(_is_rate_cb))
async def fb_rate_any(cq: CallbackQuery):
    # TODO: здесь можно сохранить оценку в БД/метрики (разбор значения из cq.data)
    try:
        await cq.answer("Спасибо! Принял 👍", show_alert=False)
    except Exception:
        pass

# ===== Запрос фразы =====
def _is_phrase_cb(data: str | None) -> bool:
    if not data:
        return False
    d = data.lower()
    # поддержим разные варианты callback_data
    return any(k in d for k in ("fb:phrase", "phrase", "comment", "text"))

# 1) Inline-кнопка «фраза»
@router.callback_query(F.data.func(_is_phrase_cb))
async def fb_phrase_inline(cq: CallbackQuery, state: FSMContext):
    await state.set_state(FeedbackStates.wait_phrase)
    await cq.message.answer(PROMPT_TEXT)
    try:
        await cq.answer()
    except Exception:
        pass

# 2) Текстовая кнопка/шорткат «✍ 1 фраза»
@router.message(StateFilter("*"), F.text == PHRASE_BUTTON_TEXT)
async def fb_phrase_text_btn(msg: Message, state: FSMContext):
    await state.set_state(FeedbackStates.wait_phrase)
    await msg.answer(PROMPT_TEXT)

# 3) Отмена во время ввода
@router.message(FeedbackStates.wait_phrase, Command("cancel"))
async def fb_phrase_cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Ок, не сохраняю. Возвращаю в меню.", reply_markup=main_menu())

# 4) Приём фразы
@router.message(FeedbackStates.wait_phrase, F.text)
async def fb_phrase_save(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()
    if not _is_short_phrase(text):
        await msg.answer("Коротко, пожалуйста (3–120 символов). Или /cancel.")
        return

    # TODO: сохранить фразу в БД/метрики
    # save_phrase(user_id=msg.from_user.id, phrase=text)

    await state.clear()
    await msg.answer(OK_SAVED, reply_markup=main_menu())

# 5) Некорректный тип сообщения в ожидании фразы
@router.message(FeedbackStates.wait_phrase)
async def fb_phrase_other(msg: Message):
    await msg.answer("Жду короткую фразу текстом. Или /cancel.")
