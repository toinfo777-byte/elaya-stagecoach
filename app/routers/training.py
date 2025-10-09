from __future__ import annotations

import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# если есть helper — используем для записи эпизода
try:
    from app.storage.repo_extras import save_training_episode
except Exception:
    save_training_episode = None  # будем просто логировать

log = logging.getLogger("training")
router = Router(name="training")

LEVEL1_TEXT = (
    "Уровень 1 · 5 мин\n\n"
    "Дыхание — 1 мин\n"
    "• Вдох на 4 — пауза 2 — выдох на 6 через «с».\n\n"
    "Рот/язык — 2 мин\n"
    "• Трель губами/языком по 20–30 сек; 10 щелчков языком.\n\n"
    "Артикуляция — 2 мин\n"
    "• «Шла Саша по шоссе…» от медленно к быстро, ставь паузы (|)."
)
LEVEL2_TEXT = (
    "Уровень 2 · 10 мин\n\n"
    "Дыхание с опорой — 3 мин\n"
    "• Вдох в бока, выдох на «ф/с», держи давление звука.\n\n"
    "Резонаторы (м-н-з) — 3 мин\n"
    "• «м» на 3–5 нот по гамме, ищем вибрацию.\n\n"
    "Текст-ритм — 4 мин\n"
    "• Абзац: 1) ровно, 2) «3-2-1», 3) с акцентами."
)
LEVEL3_TEXT = (
    "Уровень 3 · 15 мин (Про)\n\n"
    "Резонаторы — 5 мин\n"
    "• «м-н-нг» по нисходящей; 3 серии «би-бе-ба-бо-бу».\n\n"
    "Текст с паузами — 5 мин\n"
    "• 6–8 фраз. Паузы: 2|1|3|1|2|3 (сек).\n\n"
    "Микро-этюд — 5 мин\n"
    "• Тезис → мини-история (20–30 сек) → вывод."
)

class TrState(StatesGroup):
    level = State()  # '1' | '2' | '3'

def _levels_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Уровень 1"), KeyboardButton(text="Уровень 2")],
            [KeyboardButton(text="Уровень 3"), KeyboardButton(text="🏠 В меню")],
        ],
        resize_keyboard=True, input_field_placeholder="Выбери уровень…"
    )

def _done_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✅ Выполнил(а)")], [KeyboardButton(text="🏠 В меню")]],
        resize_keyboard=True
    )

# публичный вход
async def show_training_levels(message: Message, state: FSMContext):
    await state.clear()
    text = (
        "🏋️ <b>Тренировка дня</b>\n\n"
        "Выбери уровень — внутри подробные шаги.\n"
        "Когда закончишь — жми «✅ Выполнил(а)». Вернуться — «🏠 В меню»."
    )
    await message.answer(text, reply_markup=_levels_kb())

training_entry = show_training_levels
__all__ = ["router", "show_training_levels", "training_entry"]

@router.message(F.text.in_({"Уровень 1","Уровень 2","Уровень 3"}))
async def open_level(m: Message, state: FSMContext):
    mapping = {
        "Уровень 1": ("1", LEVEL1_TEXT),
        "Уровень 2": ("2", LEVEL2_TEXT),
        "Уровень 3": ("3", LEVEL3_TEXT),
    }
    lvl, text = mapping[m.text]
    await state.set_state(TrState.level)
    await state.update_data(level=lvl)
    await m.answer(text, reply_markup=_done_kb())

@router.message(F.text == "✅ Выполнил(а)")
async def done(m: Message, state: FSMContext):
    data = await state.get_data()
    level = data.get("level")
    if not level:
        await m.answer("Сначала выбери уровень 🙌", reply_markup=_levels_kb())
        return

    if save_training_episode:
        try:
            await save_training_episode(user_id=m.from_user.id, level=str(level))
            log.info("training: user=%s episode saved (level=%s)", m.from_user.id, level)
        except Exception as e:
            log.exception("training save failed: %s", e)
    else:
        log.warning("save_training_episode not available; progress not persisted")

    await m.answer("🔥 Отлично! День засчитан. Увидимся завтра!", reply_markup=_levels_kb())
    await state.clear()
