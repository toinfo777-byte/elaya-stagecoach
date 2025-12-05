from __future__ import annotations

from aiogram import Router

from .menu import router as menu_router
from .training_flow import router as training_router

router = Router()
router.include_router(menu_router)
router.include_router(training_router)
