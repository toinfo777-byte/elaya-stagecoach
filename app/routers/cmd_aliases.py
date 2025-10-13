# app/routers/cmd_aliases.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router(name="aliases")


@router.message(Command("levels", "уровни", "training"))
async def alias_training(m: Message):
    """
    Алиас на показ тренировки/уровней.
    Пытаемся импортировать старое имя show_training_levels,
    если его нет — используем новую entry-функцию.
    """
    try:
        from app.routers.training import show_training_levels as _show  # старый контракт
    except Exception:
        try:
            from app.routers.training import training_entry as _show  # новый минимал
        except Exception:
            await m.answer("Тренировка временно недоступна.")
            return
    await _show(m)


@router.message(Command("casting"))
async def alias_casting(m: Message, state: FSMContext):
    """
    Алиас на мини-кастинг.
    """
    try:
        from app.routers.minicasting import start_minicasting as _start
    except Exception:
        await m.answer("Мини-кастинг временно недоступен.")
        return
    await _start(m, state)
