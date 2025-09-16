# app/bot/handlers/feedback.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.states import FeedbackStates
from app.routers.menu import main_menu

router = Router(name="feedback2")

PHRASE_BUTTON_TEXT = "✍ 1 фраза"
PROMPT_TEXT = (
    "Напишите одну короткую фразу об этом этюде. "
    "Если передумали — отправьте /cancel."
)

RATE_EMOJI_TO_CODE = {"🔥": "hot", "👌": "ok", "😐": "meh"}
RATE_CODES = {"hot", "ok", "meh"}

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

# ---------- более «всеядный» парсер оценок ----------

def parse_rate_from_cb(data: str | None) -> str | None:
    """
    Пытается вытащить код оценки из callback_data.
    Поддерживает любой из вариантов:
      - содержит 'rate', 'feedback', 'grade', 'score', 'react', 'like'
      - слова: hot/fire/like/good/ok, meh/neutral/so_so
      - сами эмодзи 🔥/👌/😐
      - префиксы вида 'training:rate:hot', 'fb:ok', 'something|meh' и т.п.
    """
    if not data:
        return None

    # 1) если прямо эмодзи
    if data in RATE_EMOJI_TO_CODE:
        return RATE_EMOJI_TO_CODE[data]

    # 2) если в data встречаются эмодзи
    for e, code in RATE_EMOJI_TO_CODE.items():
        if e in data:
            return code

    d = data.lower()

    # 3) простые слова
    if any(k in d for k in ("hot", "fire", "🔥", "good", "like", "ok")):
        return "hot" if ("hot" in d or "fire" in d or "🔥" in d) else ("ok" if ("ok" in d or "good" in d or "like" in d) else "ok")

    if any(k in d for k in ("meh", "neutral", "so_so", "soso", "avg", "average", "neutral_face", "neutralface")):
        return "meh"

    # 4) универсальные контейнеры + явные коды
    if any(k in d for k in ("rate", "feedback", "grade", "score", "react", "like", "fb")):
        for code in RATE_CODES:
            if code in d:
                return code

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

# ---------- ОЦЕНКИ: callback (ставим ПЕРЕД хендлерами «фразы») ----------

@router.callback_query(F.data.func(lambda d: parse_rate_from_cb(d) is not None))
async def fb_rate_inline(cq: CallbackQuery):
    code = parse_rate_from_cb(cq.data)
    # TODO: сохранить оценку в БД
    try:
        await cq.answer(RATE_ALERT_TEXT.get(code, "Принято"), show_alert=False)
    except Exception:
        pass

# ---------- ОЦЕНКИ: текстом (reply-клава) ----------

@router.message(StateFilter("*"), F.text.func(lambda t: parse_rate_from_text(t) is not None))
async def fb_rate_text(msg: Message):
    code = parse_rate_from_text(msg.text)
    # TODO: сохранить оценку в БД
    await msg.answer(RATE_REPLY_TEXT.get(code, "Принято"))

# ---------- ФРАЗА ----------

def _is_phrase_cb(data: str | None) -> bool:
    if not data:
        return False
    d = data.lower()
    # не жадничаем, чтобы случайно не перехватить реакции
    return any(k in d for k in ("fb:phrase", "phrase", "comment", "text:phrase"))

@router.callback_query(F.data.func(_is_phrase_cb))
async def fb_phrase_inline(cq: CallbackQuery, state: FSMContext):
    await state.set_state(FeedbackStates.wait_phrase)
    await cq.message.answer(PROMPT_TEXT)
    try:
        await cq.answer()
    except Exception:
        pass

@router.message(StateFilter("*"), F.text == PHRASE_BUTTON_TEXT)
async def fb_phrase_text_btn(msg: Message, state: FSMContext):
    await state.set_state(FeedbackStates.wait_phrase)
    await msg.answer(PROMPT_TEXT)

@router.message(FeedbackStates.wait_phrase, Command("cancel"))
async def fb_phrase_cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Ок, не сохраняю. Возвращаю в меню.", reply_markup=main_menu())

@router.message(FeedbackStates.wait_phrase, F.text)
async def fb_phrase_save(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()
    if not _is_short_phrase(text):
        await msg.answer("Коротко, пожалуйста (3–120 символов). Или /cancel.")
        return
    # TODO: сохранить фразу
    await state.clear()
    await msg.answer("Спасибо! Принял 📝", reply_markup=main_menu())

@router.message(FeedbackStates.wait_phrase)
async def fb_phrase_other(msg: Message):
    await msg.answer("Жду короткую фразу текстом. Или /cancel.")
