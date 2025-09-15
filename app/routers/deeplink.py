# app/routers/deeplink.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import Message

# Пытаемся импортировать из shortcuts (совместимость),
# если нет — берём прямые entry-функции.
try:
    from app.routers.shortcuts import start_training_flow as _train_flow
    from app.routers.shortcuts import start_casting_flow as _cast_flow
except Exception:
    from app.routers.training import training_entry as _train_flow
    from app.routers.casting import casting_entry as _cast_flow

router = Router(name="deeplink")

def _payload(text: str | None) -> str | None:
    if not text:
        return None
    parts = text.split(maxsplit=1)
    if len(parts) == 2 and parts[0].startswith("/start"):
        return parts[1].strip()
    return None

# Точный матч по payload → обрабатываем здесь.
@router.message(StateFilter("*"), lambda m: (_payload(m.text) or "").startswith("go_training"))
async def deeplink_training(m: Message, **kwargs):
    # передаём state через kwargs, если есть
    state = kwargs.get("state")
    await _train_flow(m, state)

@router.message(StateFilter("*"), lambda m: (_payload(m.text) or "").startswith("go_casting"))
async def deeplink_casting(m: Message, **kwargs):
    state = kwargs.get("state")
    await _cast_flow(m, state)
