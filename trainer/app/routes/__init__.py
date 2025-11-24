# trainer/app/routes/__init__.py
from __future__ import annotations

from aiogram import Router

from . import menu
from . import training

# Общий роутер для бота
router = Router(name="root")

# Подключаем отдельные модули
router.include_router(menu.router)
router.include_router(training.router)

__all__ = ["router", "menu", "training"]
