from __future__ import annotations

from aiogram import Router

from . import api  # наш основной модуль с хендлерами

# Корневой роутер aiogram
router = Router(name="main")

# Подключаем подроутеры
router.include_router(api.router)

__all__ = ["router"]
