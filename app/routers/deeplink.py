# app/routers/deeplink.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router(name="deeplink")


# ВАЖНО: мы не дублируем логику тренировки/кастинга,
# а вызываем те же функции, что и обычные команды /training и /casting.
# Ниже импортируйте ровно те функции, которыми сейчас запускаются сценарии.
# Если у вас запуск делается прямо внутри обработчика, см. комментарий в shortcuts.py (п.2).
from app.routers.shortcuts import start_training_flow, start_casting_flow


async def _handle_start_payload(msg: Message, state: FSMContext, payload: str | None) -> bool:
    """
    Вернёт True, если payload распознан и сценарий запущен.
    """
    if not payload:
        return False

    p = payload.strip().lower()

    # допускаем хвосты меток: go_training_post_0915 и т.п.
    if p.startswith("go_training"):
        await msg.answer("Запускаю тренировку…")
        await start_training_flow(msg, state)  # << тот же entrypoint, что и /training
        return True

    if p.startswith("go_casting"):
        await msg.answer("Запускаю мини-кастинг…")
        await start_casting_flow(msg, state)  # << тот же entrypoint, что и /casting
        return True

    return False


@router.message(CommandStart())
async def start_with_payload(msg: Message, command: CommandObject, state: FSMContext):
    payload = (command.args or "").strip() if command else ""
    handled = await _handle_start_payload(msg, state, payload)
    if handled:
        return

    # Fallback — обычный старт без payload → дайте привет/меню как у вас принято
    await msg.answer("Привет! Напиши /menu, чтобы начать.")
