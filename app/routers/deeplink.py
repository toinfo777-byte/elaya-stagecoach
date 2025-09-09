# app/routers/deeplink.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.filters.command import CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

# входы из других модулей
from app.routers.casting import casting_entry
from app.routers.coach import coach_on

router = Router(name="deeplink")


# ⚠️ ОБРАБАТЫВАЕМ ТОЛЬКО /start С payload
@router.message(CommandStart(deep_link=True))
async def start_deeplink(m: Message, command: CommandObject, state: FSMContext):
    payload = (command.args or "").strip().lower()

    if payload in {"go_casting", "casting"}:
        return await casting_entry(m, state)

    if payload in {"coach", "go_coach", "mentor"}:
        return await coach_on(m)

    if payload in {"go_training", "training"}:
        # если хочешь — вызови тут свой вход тренировки
        return await m.answer("Открываю тренировку дня. Нажми /training")

    await m.answer("Не распознал ссылку. Открой меню: /menu")
