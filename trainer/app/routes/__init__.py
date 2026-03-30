from __future__ import annotations

from aiogram import Router

from .progress import router as progress_router
from .training_flow import router as training_flow_router
from .help import router as help_router
from .menu import router as menu_router
from .onboarding import router as onboarding_router

router = Router()

# ВАЖНО: сначала "глобальные кнопки", потом FSM/сценарии
router.include_router(progress_router)
router.include_router(menu_router)
router.include_router(help_router)
router.include_router(onboarding_router)

# FSM в конце, иначе он съедает любой текст
router.include_router(training_flow_router)
