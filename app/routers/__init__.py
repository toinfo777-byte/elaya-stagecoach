from aiogram import Router

from . import start, reviews, training

# общий корневой роутер бота
router = Router(name="root-router")

# порядок важен только логически, для нас так наглядно
router.include_router(start.router)
router.include_router(reviews.router)
router.include_router(training.router)

__all__ = (
    "router",      # корневой роутер
    "start",
    "reviews",
    "training",
)
