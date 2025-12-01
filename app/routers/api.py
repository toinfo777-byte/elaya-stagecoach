from __future__ import annotations

from fastapi import APIRouter

# Пока это просто "заглушка" под будущее API ядра.
# Важно, что файл существует и у него есть router,
# чтобы импорт в app/routers/__init__.py не ломался.

router = APIRouter()

__all__ = ["router"]
