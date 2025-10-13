# app/routers/training.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from app.keyboards.reply import main_menu_kb  # ✅ уже есть
from app.storage.repo_extras import log_progress_event  # ✅ заглушка/реализация

router = Router(name="training")


# ========= inline-клавиатуры =========
def kb_levels() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Уровень 1 • 5–8 мин", callback_data="tr:lv:1")],
        # Можно добавить позже:
        # [InlineKeyboardButton(text="Уровень 2 • скоро", callback_data="tr:lv:2:soon")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])


def kb_lv1() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выполнил(а)", callback_data="tr:lv1:done")],
        [InlineKeyboardButton(text="⟵ К уровням", callback_data="tr:back-levels")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])


# ========= публичная точка входа =========
async def show_training_levels(target: Message | CallbackQuery) -> None:
    if isinstance(target, CallbackQuery):
        await target.answer()
        m = target.message
    else:
        m = target

    await m.answer(
        "🏋️ <b>Тренировка дня</b>\n"
        "Выбери уровень — внутри подробные шаги.\n"
        "Когда закончишь — жми «✅ Выполнил(а)». Вернуться — «🏠 В меню».",
        reply_markup=kb_levels(),
    )


# ========= message-энтрипоинты =========
@router.message(StateFilter("*"), Command("levels"))
@router.message(StateFilter("*"), Command("training"))
@router.message(StateFilter("*"), F.text.regexp(r"Тренировка дня"))
async def _entry_training(msg: Message):
    await show_training_levels(msg)


# ========= callbacks =========
@router.callback_query(StateFilter("*"), F.data == "tr:back-levels")
async def _back_levels(cq: CallbackQuery):
    await show_training_levels(cq)


@router.callback_query(StateFilter("*"), F.data == "tr:lv:1")
async def _lv1_open(cq: CallbackQuery):
    await cq.answer()
    text = (
        "🎯 <b>Уровень 1 · 5–8 минут</b>\n"
        "1) 2 секунды тишины — дыхание ровное.\n"
        "2) Скажи вслух любую короткую фразу (6–8 слов).\n"
        "3) Повтори то же, но <i>чуть медленнее</i> и мягче.\n"
        "4) Поставь точку голосом, сделай паузу 1–2 сек.\n\n"
        "Готов(а)? Когда сделал(а) — жми «✅ Выполнил(а)»."
    )
    await cq.message.answer(text, reply_markup=kb_lv1())


@router.callback_query(StateFilter("*"), F.data == "tr:lv1:done")
async def _lv1_done(cq: CallbackQuery):
    await cq.answer("Зачтено!")
    # Лёгкая запись события прогресса
    try:
        await log_progress_event(cq.from_user.id, kind="training", meta={"level": 1})
    except Exception:
        pass

    await cq.message.answer(
        "Отлично! Первый шаг сделан. Возвращаю к выбору уровней — продолжишь завтра или сейчас.",
        reply_markup=kb_levels(),
    )


# ========= экспорт для других модулей =========
__all__ = ["router", "show_training_levels"]
