from __future__ import annotations

"""
Переходный слой для старого кода.

Старый бот импортирует:
    from app.routers import router as main_router

Теперь мы просто пробрасываем его к новому агрегированному
роутеру тренера из `trainer.app.routes`.
"""

from aiogram import Router

from trainer.app.routes import router as _trainer_router


# этот router будет использовать старый `app.bot.main`
router: Router = _trainer_router

__all__ = ["router"]
