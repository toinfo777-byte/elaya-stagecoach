# app/routers/training.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.reply import main_menu_kb, BTN_TRAINING

router = Router(name="training")

# ── Клавиатуры ────────────────────────────────────────────────────────────────
def kb_training_levels():
    kb = InlineKeyboardBuilder()
    kb.button(text="Уровень 1 · 5 мин",  callback_data="tr:l1")
    kb.button(text="Уровень 2 · 10 мин", callback_data="tr:l2")
    kb.button(text="Уровень 3 · 15 мин", callback_data="tr:l3")
    kb.button(text="✅ Выполнил(а)",     callback_data="tr:done")
    kb.button(text="🏠 В меню",          callback_data="go:menu")
    kb.adjust(1, 1, 1, 1, 1)
    return kb.as_markup()

def kb_done_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Выполнил(а)", callback_data="tr:done")
    kb.button(text="🏠 В меню",      callback_data="go:menu")
    kb.adjust(1, 1)
    return kb.as_markup()

# ── Контент ───────────────────────────────────────────────────────────────────
PLAN_HEADERS = {
    "l1": (
        "Новичок · 5 минут\n"
        "1) Дыхание — 1 мин\n"
        "2) Рот-язык-щелчки — 2 мин\n"
        "3) Артикуляция — 2 мин\n\n"
        "Ниже — пояснения 👇"
    ),
    "l2": (
        "Средний · 10 минут\n"
        "1) Дыхание с опорой — 3 мин\n"
        "2) Резонаторы (м-н-з) — 3 мин\n"
        "3) Текст-ритм — 4 мин\n\n"
        "Ниже — пояснения 👇"
    ),
    "l3": (
        "Про · 15 минут\n"
        "1) Резонаторы — 5 мин\n"
        "2) Текст с паузами — 5 мин\n"
        "3) Микро-этюд — 5 мин\n\n"
        "Ниже — пояснения 👇"
    ),
}

DETAILS_L1 = (
    "Дыхание — 1 мин\n"
    "• Вдох на 4 — пауза 2 — выдох на 6 через «с». Плечи расслаблены.\n\n"
    "Рот-язык-щелчки — 2 мин\n"
    "• «Трель» губами/языком по 20–30 сек; 10 чётких щелчков языком.\n\n"
    "Артикуляция — 2 мин\n"
    "• Медленно → быстро: «Шла Саша по шоссе…». Добавь паузы (|) между смысловыми кусками.\n\n"
    "Когда закончишь — жми ✅ Выполнил(а). Хочешь вернуться — 🏠 В меню."
)

DETAILS_L2 = (
    "Дыхание с опорой — 3 мин\n"
    "• Вдох вниз в бока, выдох на «ф/с», держи стабильное давление звука.\n\n"
    "Резонаторы (м-н-з) — 3 мин\n"
    "• Гудим «м» на 3–5 нот по гамме, ощущаем вибрацию в губах/носе/скуле.\n\n"
    "Текст-ритм — 4 мин\n"
    "• Прочитай абзац: первый раз ровно, второй — с паузами «3-2-1», третий — с акцентами на ключевые слова (КАПС/жест).\n\n"
    "Когда закончишь — жми ✅ Выполнил(а). Хочешь вернуться — 🏠 В меню."
)

DETAILS_L3 = (
    "Резонаторы — 5 мин\n"
    "• «м-н-нг» по нисходящей, ищем полёт без форсажа.\n"
    "• 3 серии «би-бе-ба-бо-бу» на лёгкой опоре, не залипаем в горле.\n\n"
    "Текст с паузами — 5 мин\n"
    "• Выбери 6–8 фраз. Схема пауз: 2|1|3|1|2|3 (в секундах).\n"
    "• Маркером выдели смысл, на паузе — взгляд в точку/жест.\n\n"
    "Микро-этюд — 5 мин\n"
    "• Тезис (1 фраза) → мини-история (20–30 сек) → вывод (1 фраза).\n"
    "• Сними на видео 30–45 сек. Оцени: темп, паузы, акценты.\n\n"
    "Когда закончишь — жми ✅ Выполнил(а). Хочешь вернуться — 🏠 В меню."
)

DETAILS = {"l1": DETAILS_L1, "l2": DETAILS_L2, "l3": DETAILS_L3}

# ── Публичные входы ───────────────────────────────────────────────────────────
async def training_start(msg: Message, state: FSMContext | None = None) -> None:
    if state is not None:
        await state.clear()
    await msg.answer(
        "🏋️ Тренировка дня\n\nВыбери уровень. После выполнения нажми «✅ Выполнил(а)».",
        reply_markup=kb_training_levels(),
    )

async def show_training_levels(message: Message, state: FSMContext) -> None:
    await training_start(message, state)

# алиасы совместимости
training_entry = show_training_levels

# ── Команды/кнопки входа ──────────────────────────────────────────────────────
@router.message(StateFilter("*"), Command("training"))
async def cmd_training(msg: Message, state: FSMContext):
    await training_start(msg, state)

@router.message(StateFilter("*"), F.text == BTN_TRAINING)
async def btn_training(msg: Message, state: FSMContext):
    await training_start(msg, state)

@router.callback_query(StateFilter("*"), F.data == "go:training")
async def go_training(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await training_start(cb.message, state)

# ── Планы и завершение ────────────────────────────────────────────────────────
@router.callback_query(F.data.in_({"tr:l1", "tr:l2", "tr:l3"}))
async def show_plan(cb: CallbackQuery):
    await cb.answer()
    key = cb.data.split(":")[1]
    await cb.message.answer(PLAN_HEADERS[key])
    await cb.message.answer(DETAILS[key], reply_markup=kb_done_menu())

@router.callback_query(F.data == "tr:done")
async def training_done(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    # TODO: инкремент прогресса/стрика в БД (по желанию)
    await cb.message.answer("🔥 Отлично! День засчитан. Увидимся завтра!")
    await state.clear()
    await cb.message.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())

__all__ = ["router", "show_training_levels", "training_entry", "training_start"]
