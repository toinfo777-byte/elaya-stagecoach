from __future__ import annotations

from aiogram import Router

from .menu import router as menu_router
from .training import router as training_router
from .training_flow import router as training_flow_router
from .progress import router as progress_router
from .faq import router as faq_router
from .feedback import router as feedback_router
from .extended import router as extended_router
from .onboarding import router as onboarding_router
from .help import router as help_router

# Единый агрегированный роутер тренера
router = Router(name="trainer")

# Порядок важен: сначала "вход", потом основное, потом доп. сервис
router.include_router(onboarding_router)
router.include_router(menu_router)
router.include_router(training_router)
router.include_router(training_flow_router)
router.include_router(progress_router)
router.include_router(faq_router)
router.include_router(feedback_router)
router.include_router(extended_router)
router.include_router(help_router)
