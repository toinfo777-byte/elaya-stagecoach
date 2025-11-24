# app/routes/api.py
from __future__ import annotations

from typing import Dict, Union

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/healthz")
@router.get("/healthhz")  # alias под опечатку в Render health-check
def healthz() -> Dict[str, Union[bool, str]]:
    """
    Простой health-check.

    /api/healthz  — нормальный путь
    /api/healthhz — алиас для Render, который сейчас шлёт запрос именно сюда.
    """
    return {"ok": True, "status": "healthy"}
