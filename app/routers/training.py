from __future__ import annotations

import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# Пишем прогресс через доп. helper (как мы обсуждали ранее)
try:
    from app.storage.repo_extras import save_training_episode
except Exception:
    save_training_episode = None  # если нет файла — просто логируем

log = logging.getLogger("training")
router = Router(name="training_reply")

# ───────────────────────────── тексты уровней ─────────────────────────────
LEVEL1_TEXT = (
    "Уровень 1 · 5 мин\n\n"
    "Дыхание — 1 мин\n"
    "• Вдох на 4 — пауза 2 — выдох на 6 через «с». Плечи расслаблены.\n\n"
    "Рот-язык-щелчки — 2 мин\n"
    "• «Трель» губами/языком по 20–30 сек; 10 щелчков языком.\n\n"
    "Артикуляция — 2 мин\n"
    "• Медленно → быстро: «Шла Саша по шоссе…». Ставь паузы (|)."
)
LEVEL2_TEXT = (
    "Уровень 2 · 10 мин\n\n"
    "Дыхание с опорой — 3 мин\n"
    "• Вдох вниз в бока, выдох на «ф/с», держи давление звука.\n\n"
    "Резонаторы (м-н-з) — 3 мин\n"
    "• «м» на 3–5 нот по гамме, ощущай вибрацию.\n\n"
    "Текст-ритм — 4 мин\n"
    "• Абзац: 1) ровно, 2) «3-2-1», 3) акценты на ключевые слова."
)
LEVEL3_TEXT = (
    "Уровень 3 · 15 мин (Про)\n\n"
    "Резонаторы — 5 мин\n"
    "• «м-н-нг» по нисходящей; серии «би-бе-ба-бо-бу» на лёгкой опоре.\n\n"
    "Текст с паузами — 5 мин\n"
    "• 6–8 фраз. Паузы: 2|1|3|1|2|3 (сек). На паузе — взгляд/жест.\n\n"
    "Микро-этюд — 5 мин\n"
    "• Тезис → мини-история (20–30 сек) → вывод. Сними 30–45 сек."
)

# ───────────────────────────── состояние ─────────────────────────────
class TrState(StatesGroup):
    level = State()   # '1' | '2' | '3'

# ───────────────────────────── клавиатуры ─────────────────────────────
def _levels_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="Уровень 1"), KeyboardButton(text="Уровень 2")],
        [KeyboardButton(text="Уровень 3"), KeyboardButton(text="🏠 В меню")],
    ]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=rows, input_field_placeholder="Выбери уровень…")

def _done_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="✅ Выполнил(а)")],
        [KeyboardButton(text="🏠 В меню")],
    ]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=rows)

# ───────────────────────────── публичный вход ─────────────────────────────
async def show_training_levels(message: Message, state: FSMContext):
    await state.clear()
    text = (
        "🏋️ Тренировка дня\n\n"
        "Выбери уровень — внутри подробные шаги. Когда закончишь — жми «✅ Выполнил(а)».\n"
        "Вернуться — «🏠 В меню»."
    )
    await message.answer(text, reply_markup=_levels_kb())

# Совместимый алиас
training_entry = show_training_levels
__all__ = ["router", "show_training_levels", "training_entry"]

# ───────────────────────────── выбор уровней ─────────────────────────────
@router.message(F.text.in_({"Уровень 1", "Уровень 2", "Уровень 3"}))
async def training_open_level(m: Message, state: FSMContext):
    mapping = {"Уровень 1": ("1", LEVEL1_TEXT), "Уровень 2": ("2", LEVEL2_TEXT), "Уровень 3": ("3", LEVEL3_TEXT)}
    lvl, text = mapping[m.text]
    await state.set_state(TrState.level)
    await state.update_data(level=lvl)
    await m.answer(text, reply_markup=_done_kb())

@router.message(F.text == "✅ Выполнил(а)")
async def training_done(m: Message, state: FSMContext):
    data = await state.get_data()
    level = data.get("level")
    if not level:
        await m.answer("Сначала выбери уровень 🙌", reply_markup=_levels_kb())
        return

    # Пишем эпизод
    if save_training_episode:
        try:
            await save_training_episode(user_id=m.from_user.id, level=str(level))
            log.info("training: user=%s episode saved (level=%s)", m.from_user.id, level)
        except Exception as e:
            log.exception("training save failed: %s", e)
    else:
        log.warning("save_training_episode not available; progress is not persisted")

    await m.answer("🔥 Отлично! День засчитан. Увидимся завтра!", reply_markup=_levels_kb())
    # Сброс текущего уровня, чтобы не засчитать повторно
    await state.clear()
