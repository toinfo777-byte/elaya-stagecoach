# app/routers/__init__.py
# Экспортируем подключаемые роутеры, чтобы main мог их импортировать
from . import system, hq

__all__ = ["system", "hq"]

