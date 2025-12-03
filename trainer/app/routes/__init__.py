from __future__ import annotations

from aiogram import Router

from .training_flow import router as training_flow_router
from .system import router as system_router
from .menu import router as menu_router

router = Router(name="root")

# ВАЖНО: порядок
router.include_router(training_flow_router)   # FSM — всегда первая
router.include_router(system_router)          # служебные эндпоинты
router.include_router(menu_router)            # кнопки, навигация
