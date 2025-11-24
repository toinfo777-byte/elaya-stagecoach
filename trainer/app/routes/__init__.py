# trainer/app/routes/__init__.py
from __future__ import annotations

from aiogram import Router

from .start import router as start_router
from .training_flow import router as training_router

router = Router(name="root")

# порядок важен: сначала /start, потом тренировка
router.include_router(start_router)
router.include_router(training_router)
