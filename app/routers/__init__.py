from __future__ import annotations

from fastapi import APIRouter

from .api import router as api_router
from .system import router as system_router
from .ui import router as ui_router
# если у тебя ещё есть menu / hq и т.п. — их тоже оставляем
# from .menu import router as menu_router
# from .hq import router as hq_router

router = APIRouter()

router.include_router(api_router)
router.include_router(system_router)
router.include_router(ui_router)
# и тут же, если есть:
# router.include_router(menu_router)
# router.include_router(hq_router)
