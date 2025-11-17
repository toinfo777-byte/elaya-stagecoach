from aiogram import Router

from .start import router as start_router
from .reviews import router as reviews_router
from .training import router as training_router

# общий корневой роутер бота
router = Router(name="root-router")

# порядок важен только логически, для нас так наглядно
router.include_router(start_router)
router.include_router(reviews_router)
router.include_router(training_router)

__all__ = (
    "router",
    "start_router",
    "reviews_router",
    "training_router",
)
