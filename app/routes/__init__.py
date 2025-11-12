# app/routes/__init__.py
from .ui import router as ui_router
from .system import router as system_router

__all__ = ["ui_router", "system_router"]
