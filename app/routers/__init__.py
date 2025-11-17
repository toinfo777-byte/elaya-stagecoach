from aiogram import Router

from .start import router as start_router
from .training import router as training_router
from .reviews import router as reviews_router

router = Router(name="root")

# Подключаем все дочерние роутеры РОВНО ОДИН РАЗ
router.include_router(start_router)
router.include_router(training_router)
router.include_router(reviews_router)

__all__ = ["router"]
