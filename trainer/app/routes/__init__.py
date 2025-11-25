from aiogram import Router

from . import menu, training_flow

router = Router(name="root-router")

router.include_router(menu.router)
router.include_router(training_flow.router)

__all__ = ["router"]
