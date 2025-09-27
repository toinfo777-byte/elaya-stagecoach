# app/routers/training.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router(name="training")  # <-- main.py ждёт r_training.router

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

L1_TEXT = (
    "Уровень 1 · 5 мин\n\n"
    "Дыхание — 1 мин\n"
    "• Вдох 4 — пауза 2 — выдох 6 через «с».\n\n"
    "Рот-язык-щелчки — 2 мин\n"
    "• Трель губ/языка по 20–30 сек; 10 щелчков языком.\n\n"
    "Артикуляция — 2 мин\n"
    "• «Шла Саша по шоссе…» от медленно к быстро, с паузами.\n\n"
    "Когда закончишь — жми «✅ Выполнил(а)»."
)
L2_TEXT = (
    "Уровень 2 · 10 мин\n\n"
    "Дыхание с опорой — 3 мин\n"
    "• Вдох в бока, выдох на «ф/с», стабильное давление.\n\n"
    "Резонаторы (м-н-з) — 3 мин\n"
    "• «м» по 3–5 нот, ощущение вибрации.\n\n"
    "Текст-ритм — 4 мин\n"
    "• Прочитай абзац: ровно → с паузами «3-2-1» → с акцентами.\n\n"
    "Готов? Нажми «✅ Выполнил(а)»."
)
L3_TEXT = (
    "Уровень 3 · 15 мин (Про)\n\n"
    "Резонаторы — 5 мин\n"
    "• «м-н-нг» по нисходящей; 3 серии «би-бе-ба-бо-бу».\n\n"
    "Текст с паузами — 5 мин\n"
    "• 6–8 фраз со схемой пауз 2|1|3|1|2|3.\n\n"
    "Микро-этюд — 5 мин\n"
    "• Тезис → мини-история 20–30 сек → вывод.\n\n"
    "Как закончишь — «✅ Выполнил(а)»."
)

async def show_training_levels(message: Message):
    await message.answer(
        "🏋️ Тренировка дня\n\nВыбери уровень. После выполнения нажми «✅ Выполнил(а)».",
        reply_markup=_levels_kb(),
    )

# alias как в старом коде
training_entry = show_training_levels

@router.message(Command("training"))
async def cmd_training(m: Message):
    await show_training_levels(m)

@router.callback_query(F.data == "tr:l1")
async def cb_l1(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer(L1_TEXT, reply_markup=_done_kb())

@router.callback_query(F.data == "tr:l2")
async def cb_l2(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer(L2_TEXT, reply_markup=_done_kb())

@router.callback_query(F.data == "tr:l3")
async def cb_l3(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer(L3_TEXT, reply_markup=_done_kb())

@router.callback_query(F.data == "tr:done")
async def cb_done(cb: CallbackQuery):
    await cb.answer("Засчитано!")
    # необязательно: лог прогресса (если функция есть)
    try:
        from app.storage.repo_extras import log_progress_event
        await log_progress_event(cb.from_user.id, kind="training", meta=None)
    except Exception:
        pass
    from app.routers.help import show_main_menu
    await show_main_menu(cb)
