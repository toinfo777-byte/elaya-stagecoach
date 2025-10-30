# Удобные реэкспорты
from . import config  # значения INTRO/REFLECT/TRANSITION
from . import manager  # SceneManager
from .intro import router as intro_router
from .reflect import router as reflect_router
from .transition import router as transition_router

__all__ = [
    "config",
    "manager",
    "intro_router",
    "reflect_router",
    "transition_router",
]
