# app/routers/debug.py
from __future__ import annotations

import logging
from aiogram import Router

router = Router(name="debug")
log = logging.getLogger(__name__)

# Логируем апдейты через middleware TraceAllMiddleware в main.py.
# ВАЖНО: НЕ перехватываем callback_query и НЕ отвечаем "OK",
# иначе реальные колбэки (оценки/фраза) не дойдут до своих хендлеров.
