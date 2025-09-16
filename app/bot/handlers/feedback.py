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

# Набор оценок, если приходят текстом (reply-клава)
RATE_EMOJI_TO_CODE = {
    "🔥": "hot",
    "👌": "ok",
    "😐": "meh",
}
RATE_CODES = {"hot", "ok", "meh"}

# Ответы на разные оценки
RATE_REPLY_TEXT = {
    "hot": "🔥 Отлично! Записал.",
    "ok":  "👌 Принято. Спасибо!",
    "meh": "😐 Ок, учтено.",
}
RATE_ALERT_TEXT = {
    "hot": "🔥 Отлично! Записал.",
    "ok":  "👌 Принято.",
    "meh": "😐 Учтено.",
}

def _is_short_phrase(text: str) -> bool:
    t = (text or "").strip()
    return 3 <= len(t) <= 120 and not t.startswith("/")

# ---------- parsing helpers ----------

def parse_rate_from_cb(data: str | None) -> str | None:
    """
    Пытаемся вытащить код оценки из callback_data.
    Поддерживаем форматы:
      - 'fb:rate:hot', 'rate:ok', 'training:rate:meh'
      - 'feedback:hot', 'hot', 'ok', 'meh'
      - эмодзи внутри callback_data: '🔥' / '👌' / '😐'
    Возвращаем 'hot' | 'ok' | 'meh' | None
    """
    if not data:
        return None
    d = data.lower()

    # прямые коды
    if d in RATE_CODES:
        return d

    # с префиксами
    if any(k in d for k in ("rate", "fb:rate", "feedback", "fb", "grade", "score")):
        for code in RATE_CODES:
            if code in d:
                return code

    # если прислали эмодзи в data
    for emoji, code in RATE_EMOJI_TO_CODE.items():
        if emoji in data:
            return code

    # fallback: один символ в data — тоже эмодзи?
    if data in RATE_EMOJI_TO_CODE:
        return RATE_EMOJI_TO_CODE[data]

    return None

def parse_rate_from_text(text: str | None) -> str | None:
    if not text:
        return None
    t = text.strip()
    if t in RATE_EMOJI_TO_CODE:
        return RATE_EMOJI_TO_CODE[t]
    low = t.lower()
    if low in RATE_CODES:
        return low
    return None

# ---------- ОЦЕНКИ: inline (callback) ----------

@router.callback_query(F.data.func(lambda d: parse_rate_from_cb(d) is not None))
async def fb_rate_inline(cq: CallbackQuery):
    code = parse_rate_from_cb(cq.data)
    # TODO: здесь можно сохранить оценку (user_id=cq.from_user.id, code)
    try:
        await cq.answer(RATE_ALERT_TEXT.get(code, "Принято"), show_alert=False)
    except Exception:
        pass

# ---------- ОЦЕНКИ: текстом (reply-клавиатура) ----------

@router.message(StateFilter("*"), F.text.func(lambda t: parse_rate_from_text(t) is not None))
async def fb_rate_text(msg: Message):
    code = parse_rate_from_text(msg.text)
    # TODO: сохранить оценку (user_id=msg.from_user.id, code)
    await msg.answer(RATE_REPLY_TEXT.get(code, "Принято"))

# ---------- ФРАЗА ----------

def _is_phrase_cb(data: str | None) -> bool:
    if not data:
        return False
    d = data.lower()
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
    await msg.answer("Спасибо! Принял 📝", reply_markup=main_menu())

# 5) Некорректный тип сообщения в ожидании фразы
@router.message(FeedbackStates.wait_phrase)
async def fb_phrase_other(msg: Message):
    await msg.answer("Жду короткую фразу текстом. Или /cancel.")
