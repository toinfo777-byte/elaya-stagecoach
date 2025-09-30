from __future__ import annotations

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# если router уже определён — не дублируем
try:
    router  # noqa: F821
except NameError:
    router = Router(name="training")

# ── тексты уровней ───────────────────────────────────────────────────────────
LEVEL1_TEXT = (
    "Уровень 1 · 5 мин\n\n"
    "Дыхание — 1 мин\n"
    "• Вдох на 4 — пауза 2 — выдох на 6 через «с». Плечи расслаблены.\n\n"
    "Рот-язык-щелчки — 2 мин\n"
    "• «Трель» губами/языком по 20–30 сек; 10 чётких щелчков языком.\n\n"
    "Артикуляция — 2 мин\n"
    "• Медленно → быстро: «Шла Саша по шоссе…». Добавь паузы (|) между смысловыми кусками."
)

LEVEL2_TEXT = (
    "Уровень 2 · 10 мин\n\n"
    "Дыхание с опорой — 3 мин\n"
    "• Вдох вниз в бока, выдох на «ф/с», держи стабильное давление звука.\n\n"
    "Резонаторы (м-н-з) — 3 мин\n"
    "• Гудим «м» на 3–5 нот по гамме, ощущаем вибрацию в губах/носе/скуле.\n\n"
    "Текст-ритм — 4 мин\n"
    "• Прочитай абзац: 1) ровно, 2) с паузами «3-2-1», 3) с акцентами на ключевые слова."
)

LEVEL3_TEXT = (
    "Уровень 3 · 15 мин (Про)\n\n"
    "Резонаторы — 5 мин\n"
    "• «м-н-нг» по нисходящей, ищем полёт без форсажа.\n"
    "• 3 серии «би-бе-ба-бо-бу» на лёгкой опоре, не залипаем в горле.\n\n"
    "Текст с паузами — 5 мин\n"
    "• Выбери 6–8 фраз. Схема пауз: 2|1|3|1|2|3 (в секундах). На паузе — взгляд/жест.\n\n"
    "Микро-этюд — 5 мин\n"
    "• Тезис (1 фраза) → мини-история (20–30 сек) → вывод (1 фраза). "
    "Сними 30–45 сек, оцени: темп, паузы, акценты."
)

def _levels_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Уровень 1", callback_data="tr:level:1")],
        [InlineKeyboardButton(text="Уровень 2", callback_data="tr:level:2")],
        [InlineKeyboardButton(text="Уровень 3", callback_data="tr:level:3")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])

def _done_kb(level: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выполнил(а)", callback_data=f"tr:done:{level}")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])

# ── публичный вход ───────────────────────────────────────────────────────────
async def show_training_levels(message: Message, state: FSMContext):
    """Показать уровни тренировки (используется и в диплинке)."""
    await state.clear()
    text = (
        "🏋️ Тренировка дня\n\n"
        "Выбери уровень — внутри подробные шаги. "
        "Когда закончишь — жми «✅ Выполнил(а)». "
        "Хочешь вернуться — «🏠 В меню»."
    )
    await message.answer(text, reply_markup=_levels_kb())

# совместимый алиас под старые импорты
training_entry = show_training_levels

__all__ = ["router", "show_training_levels", "training_entry"]

# ── хендлеры уровней/выполнения ──────────────────────────────────────────────
@router.callback_query(F.data.startswith("tr:level:"))
async def training_show_level(cq: CallbackQuery):
    await cq.answer()
    level = cq.data.split(":")[-1]
    mapping = {"1": LEVEL1_TEXT, "2": LEVEL2_TEXT, "3": LEVEL3_TEXT}
    text = mapping.get(level, "План скоро обновим 🙂")

    await cq.message.answer(text, reply_markup=_done_kb(level))

@router.callback_query(F.data.startswith("tr:done:"))
async def training_done(cq: CallbackQuery):
    await cq.answer("Засчитано!")
    level = cq.data.split(":")[-1]

    # пробуем сохранить эпизод, если есть ваша обёртка
    try:
        from app.storage.repo_extras import save_training_episode
        await save_training_episode(user_id=cq.from_user.id, level=level)
    except Exception:
        pass

    await cq.message.answer("🔥 Отлично! День засчитан. Увидимся завтра!")

    # сразу возвращаем в меню тем же способом, как при /start
    try:
        from app.routers.help import show_main_menu
        await show_main_menu(cq)
    except Exception:
        # если вдруг что-то не импортировалось — просто кнопка назад уже есть
        pass
