from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from app.routers.help import show_main_menu
try:
    from app.storage.repo_extras import log_progress_event  # опционально
except Exception:
    async def log_progress_event(*args, **kwargs):  # заглушка
        return None

tr_router = Router(name="training")


def _levels_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Уровень 1", callback_data="tr:l1")],
        [InlineKeyboardButton(text="Уровень 2", callback_data="tr:l2")],
        [InlineKeyboardButton(text="Уровень 3", callback_data="tr:l3")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])

def _done_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выполнил(а)", callback_data="tr:done")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])


async def show_training_levels(obj: Message | CallbackQuery):
    text = (
        "🏋️ Тренировка дня\n\n"
        "Выбери уровень. После выполнения нажми «✅ Выполнил(а)»."
    )
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        await obj.message.answer(text, reply_markup=_levels_kb())
    else:
        await obj.answer(text, reply_markup=_levels_kb())


LEVELS = {
    "tr:l1": (
        "Уровень 1 · 5 мин\n\n"
        "Дыхание — 1 мин\n• Вдох 4 — пауза 2 — выдох 6 на «с».\n\n"
        "Рот-язык-щелчки — 2 мин\n• Трель губами/языком 20–30 сек; 10 щелчков.\n\n"
        "Артикуляция — 2 мин\n• «Шла Саша по шоссе…» от медленно к быстро.\n\n"
        "Когда закончишь — жми «✅ Выполнил(а)»."
    ),
    "tr:l2": (
        "Уровень 2 · 10 мин\n\n"
        "Дыхание с опорой — 3 мин\n• Вдох вниз в бока, выдох на «ф/с».\n\n"
        "Резонаторы (м-н-з) — 3 мин\n• «м» на 3–5 нот, ищем вибрацию.\n\n"
        "Текст–ритм — 4 мин\n• Абзац ровно → с паузами 3–2–1 → с акцентами.\n\n"
        "Когда закончишь — жми «✅ Выполнил(а)»."
    ),
    "tr:l3": (
        "Уровень 3 · 15 мин (Про)\n\n"
        "Резонаторы — 5 мин\n• «м-н-нг» по нисходящей, полёт без форсажа.\n\n"
        "Текст с паузами — 5 мин\n• 6–8 фраз, схема пауз 2|1|3|1|2|3.\n\n"
        "Микро-этюд — 5 мин\n• Тезис → мини-история (20–30 сек) → вывод.\n\n"
        "Когда закончишь — жми «✅ Выполнил(а)»."
    ),
}

@tr_router.callback_query(F.data.in_(LEVELS.keys()))
async def tr_level(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer(LEVELS[cb.data], reply_markup=_done_kb())

@tr_router.callback_query(F.data == "tr:done")
async def tr_done(cb: CallbackQuery):
    await cb.answer("Засчитано!")
    try:
        await log_progress_event(cb.from_user.id, kind="training", meta={})
    except Exception:
        pass
    await cb.message.answer("🔥 Отлично! День засчитан. Увидимся завтра!")
    await show_main_menu(cb)
