# app/routers/settings.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# ── МИНИМАЛ БЕЗ ВНЕШНИХ ЗАВИСИМОСТЕЙ ─────────────────────────────────────────
router = Router(name="settings")

def _settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Удалить мои данные (заглушка)", callback_data="set:del:ask")],
        [InlineKeyboardButton(text="Закрыть", callback_data="set:close")],
    ])

def _confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да, удалить", callback_data="set:del:yes"),
            InlineKeyboardButton(text="Отмена", callback_data="set:del:no"),
        ]
    ])

# ── ХЕНДЛЕРЫ ─────────────────────────────────────────────────────────────────
@router.message(Command("settings"))
async def show_settings(m: Message):
    await m.answer(
        "⚙️ <b>Настройки</b>\n\n"
        "— Здесь позже появятся расширенные опции.\n"
        "— Удаление данных сейчас выполнится как заглушка (no-op).",
        reply_markup=_settings_kb(),
    )

@router.callback_query(F.data == "set:close")
async def close_settings(cb: CallbackQuery):
    await cb.answer("Закрыто")
    await cb.message.edit_text("Настройки закрыты.")

@router.callback_query(F.data == "set:del:ask")
async def ask_delete(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer(
        "❗️ Подтвердите удаление данных. Сейчас это заглушка (ничего не удаляет).",
        reply_markup=_confirm_kb(),
    )

@router.callback_query(F.data == "set:del:no")
async def cancel_delete(cb: CallbackQuery):
    await cb.answer("Отмена")
    await cb.message.answer("Ок, ничего не удаляю.")

@router.callback_query(F.data == "set:del:yes")
async def do_delete(cb: CallbackQuery):
    await cb.answer("Готово")
    # заглушка — реально ничего не делаем
    await cb.message.answer("Данные «удалены» (заглушка).")
