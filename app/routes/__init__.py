# app/routes/__init__.py
from __future__ import annotations

from fastapi import APIRouter

from .system import router as system_router
# если ui.py и api.py тоже используют FastAPI-роутеры — подключим и их
try:
    from .ui import router as ui_router
except ImportError:  # вдруг там что-то другое
    ui_router = None

try:
    from .api import router as api_router
except ImportError:
    api_router = None

router = APIRouter()

# 1) системные эндпоинты: /api/event, /api/timeline, /api/health
router.include_router(system_router)

# 2) UI-маршруты (если есть)
if ui_router is not None:
    router.include_router(ui_router)

# 3) дополнительные /api-ручки (если есть)
if api_router is not None:
    router.include_router(api_router)
