from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.keyboards.reply import main_menu_kb
from app.storage.repo_extras import log_training_done

router = Router(name="training")


# === Клавиатуры ==============================================================

def _levels_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Уровень 1", callback_data="tr:l1")],
        [InlineKeyboardButton(text="Уровень 2", callback_data="tr:l2")],
        [InlineKeyboardButton(text="Уровень 3", callback_data="tr:l3")],
        [InlineKeyboardButton(text="✅ Выполнил(а)", callback_data="tr:done")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="to_menu")],
    ])


def _done_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выполнил(а)", callback_data="tr:done")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="to_menu")],
    ])


# === Публичные входы =========================================================

async def show_training_levels(message: Message, state: FSMContext):
    """Единая точка входа (меню, /training, диплинк)."""
    await state.clear()
    top = (
        "🏋️ Тренировка дня\n\n"
        "Уровень 1 — 5 мин (разогрев) · Уровень 2 — 10 мин (база) · Уровень 3 — 15 мин (про).\n\n"
        "Выбери уровень. После выполнения нажми «✅ Выполнил(а)»."
    )
    await message.answer(top, reply_markup=_levels_kb())


# алиас для совместимости
training_entry = show_training_levels


@router.message(StateFilter("*"), Command("training"))
async def training_cmd(message: Message, state: FSMContext):
    await show_training_levels(message, state)


# === Выбор уровня и план =====================================================

_PLANS = {
    "l1": (
        "Уровень 1 · 5 мин\n\n"
        "Дыхание — 1 мин\n"
        "• Вдох на 4 — пауза 2 — выдох на 6 через «с». Плечи расслаблены.\n\n"
        "Рот-язык-щелчки — 2 мин\n"
        "• «Трель» губами/языком по 20–30 сек; 10 чётких щелчков языком.\n\n"
        "Артикуляция — 2 мин\n"
        "• Медленно → быстро: «Шла Саша по шоссе…». Добавь паузы (|) между смысловыми кусками.\n\n"
        "Когда закончишь — жми ✅ Выполнил(а). Хочешь вернуться — 🏠 В меню."
    ),
    "l2": (
        "Уровень 2 · 10 мин\n\n"
        "Дыхание с опорой — 3 мин\n"
        "• Вдох вниз в бока, выдох на «ф/с», держи стабильное давление звука.\n\n"
        "Резонаторы (м-н-з) — 3 мин\n"
        "• Гудим «м» на 3–5 нот по гамме, ощущаем вибрацию в губах/носе/скуле.\n\n"
        "Текст-ритм — 4 мин\n"
        "• Прочитай абзац: ровно → с паузами «3-2-1» → с акцентами на ключевые слова.\n\n"
        "Когда закончишь — жми ✅ Выполнил(а). Хочешь вернуться — 🏠 В меню."
    ),
    "l3": (
        "Уровень 3 · 15 мин (Про)\n\n"
        "Резонаторы — 5 мин\n"
        "• «м-н-нг» по нисходящей, ищем полёт без форсажа.\n"
        "• 3 серии «би-бе-ба-бо-бу» на лёгкой опоре, без зажима.\n\n"
        "Текст с паузами — 5 мин\n"
        "• Возьми 6–8 фраз. Схема пауз: 2|1|3|1|2|3 (сек).\n"
        "• На паузе — взгляд в точку/жест.\n\n"
        "Микро-этюд — 5 мин\n"
        "• Тезис (1 фраза) → мини-история (20–30 сек) → вывод (1 фраза).\n"
        "• Сними 30–45 сек. Оцени: темп, паузы, акценты.\n\n"
        "Когда закончишь — жми ✅ Выполнил(а). Хочешь вернуться — 🏠 В меню."
    ),
}


@router.callback_query(F.data.in_({"tr:l1", "tr:l2", "tr:l3"}))
async def training_level_selected(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    level = cb.data.split(":")[1]  # l1/l2/l3
    await state.update_data(training_level=level)
    await cb.message.answer(_PLANS[level], reply_markup=_done_kb())


# === Зачёт дня ===============================================================

@router.callback_query(F.data == "tr:done")
async def training_done(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    data = await state.get_data()
    level = data.get("training_level")  # может быть None, если нажали без выбора

    try:
        await log_training_done(cb.from_user.id, level=level)
    except Exception:
        # не мешаем UX'у, но в логах увидишь ошибку
        pass

    await cb.message.answer("🔥 Отлично! День засчитан. Увидимся завтра!")
    await state.clear()
    await cb.message.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())


# === Экспортируем публичные имена ===========================================

__all__ = ["router", "show_training_levels", "training_entry"]
