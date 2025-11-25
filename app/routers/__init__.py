from fastapi import APIRouter
from . import api, system, ui

router = APIRouter()

router.include_router(api.router)
router.include_router(system.router)
router.include_router(ui.router)

__all__ = ["router"]
