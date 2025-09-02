import logging
from aiogram import BaseMiddleware
from aiogram.types import Update
from typing import Callable, Awaitable, Any

logger = logging.getLogger(__name__)

class ErrorsMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Update, dict], Awaitable[Any]], event: Update, data: dict):
        try:
            return await handler(event, data)
        except Exception as e:
            logger.exception("Unhandled error: %s", e)
