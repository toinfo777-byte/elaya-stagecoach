# app/routers/__init__.py
"""
Пакет роутеров.

Важно: избегаем сайд-эффектов (авто-импортов), чтобы профили
подключались строго из app/main.py.
"""

# Эти модули безопасно импортировать всегда (служебные/HQ)
from . import system, hq  # noqa: F401

# debug-роутер оставляем опционально: подключай вручную в main.py при необходимости
try:  # если файла нет — пропускаем
    from . import debug  # noqa: F401
except Exception:
    debug = None  # type: ignore

__all__ = ["system", "hq", "debug"]
