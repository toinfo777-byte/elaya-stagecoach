from __future__ import annotations
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

router = Router(name="callback_probe")
log = logging.getLogger("probe")

def _probe_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔘 test (probe)", callback_data="probe:ping")],
        [InlineKeyboardButton(text="🏋️ Тренировка дня", callback_data="go:training")],
        [InlineKeyboardButton(text="📈 Мой прогресс",   callback_data="go:progress")],
    ])

@router.message(Command("probe"))
async def cmd_probe(m: Message):
    await m.answer("·", reply_markup=ReplyKeyboardRemove())
    await m.answer("probe: нажми любую кнопку ниже — я должен отлогировать callback", reply_markup=_probe_kb())

# Ловим ЛЮБОЙ callback_query без фильтров и логируем
@router.callback_query()
async def any_callback(cq: CallbackQuery):
    data = (cq.data or "").strip()
    log.info("probe callback: %r", data)
    # краткий ответ, чтобы пользователь видел, что кнопка «прожалась»
    await cq.answer(f"cb: {data[:32]}", show_alert=False)

    # На всякий случай — немного эха в чат (не спамим)
    if data.startswith(("probe:", "go:")):
        await cq.message.answer(f"probe ✓ получен callback: <code>{data}</code>")
