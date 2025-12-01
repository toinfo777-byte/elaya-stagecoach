from __future__ import annotations

from aiogram import Router

from .training_flow import router as training_router
from .progress import router as progress_router
from .extended import router as extended_router

# ВАЖНО: создаём ИМЕННО ЭКЗЕМПЛЯР Router, а не ссылаемся на класс
router: Router = Router(name="root")

# порядок не критичен, но так логично:
router.include_router(training_router)
router.include_router(progress_router)
router.include_router(extended_router)
