# app/bot/main.py
from __future__ import annotations

import asyncio
import logging

from fastapi import FastAPI

# Берём основной тренерский main из пакета trainer
from app....main import main as trainer_main

logger = logging.getLogger(__name__)

app = FastAPI(title="Elaya Trainer Bot Wrapper")


@app.get("/healthz")
async def root_healthz() -> dict:
    """
    Простой healthcheck для Render.
    """
    return {"status": "ok"}


@app.get("/api/healthz")
async def api_healthz() -> dict:
    """
    Совместимость с уже настроенным путём healthcheck'а.
    """
    return {"status": "ok"}


@app.on_event("startup")
async def startup_trainer() -> None:
    """
    На старте FastAPI поднимаем тренер-бота как фоновой таск.
    """
    logger.info("Starting trainer bot background task...")
    # trainer_main — async def, поэтому запускаем его как фоновую задачу
    asyncio.create_task(trainer_main())
