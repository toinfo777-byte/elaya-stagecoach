from __future__ import annotations
from typing import Any, Awaitable, Callable

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

# вызываем ПУБЛИЧНЫЕ функции из ваших модулей
from app.routers.training import show_training_levels
from app.routers.minicasting import start_minicasting

router = Router(name="cmd_aliases")
__all__ = ["router"]

async def _safe_call(fn: Callable[..., Awaitable[Any]], obj: Message, state: FSMContext) -> Any:
    """
    Универсальный безопасный вызов: сначала (obj, state), если TypeError — (obj).
    Нужно, потому что в одних ваших модулях state обязателен, в других — нет.
    """
    try:
        return await fn(obj, state)   # type: ignore[misc]
    except TypeError:
        return await fn(obj)          # type: ignore[misc]

@router.message(StateFilter("*"), Command("training"))
async def cmd_training(m: Message, state: FSMContext):
    await state.clear()
    await _safe_call(show_training_levels, m, state)

@router.message(StateFilter("*"), Command("casting"))
async def cmd_casting(m: Message, state: FSMContext):
    await state.clear()
    await _safe_call(start_minicasting, m, state)
