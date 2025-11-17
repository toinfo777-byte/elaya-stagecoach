from .start import router as start_router
from .reviews import router as reviews_router
from .training import router as training_router

__all__ = (
    "start_router",
    "reviews_router",
    "training_router",
)
