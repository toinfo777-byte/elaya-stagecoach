from __future__ import annotations
import logging
from aiogram import Router, F
from aiogram.types import Message

router = Router(name="debug")
log = logging.getLogger("elaya.debug")

# ❗ ВАЖНО: не блокируем цепочку других хендлеров
@router.message(F.text, flags={"block": False})
async def log_any(msg: Message) -> None:
    # Короткий безопасный лог — только мета
    log.info(
        "[DBG] update chat=%s(%s) user=%s text=%r",
        msg.chat.type, msg.chat.id, getattr(msg.from_user, "id", None), msg.text
    )
