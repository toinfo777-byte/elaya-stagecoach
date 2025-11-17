from __future__ import annotations

from aiogram import Router

from . import start  # сюда потом добавим: menu, reviews, progress, help, policy и т.д.

router = Router(name="root")

# базовый /start
router.include_router(start.router)

__all__ = ["router"]
