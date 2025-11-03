from __future__ import annotations

import logging
from aiogram import Router
from aiogram.types import Message

# ВАЖНО:
# 1) Логируем только message-апдейты, чтобы не мешать callback_query хендлерам.
# 2) Удалить этот роутер после отладки, чтобы не засорять логи.

router = Router(name="debug")
log = logging.getLogger("elaya.debug")


@router.message()  # без фильтров — ловим все сообщения (private/group/supergroup)
async def log_any(msg: Message):
    text = msg.text or msg.caption or "<non-text>"
    chat_kind = getattr(msg.chat.type, "value", str(msg.chat.type))
    log.info("[DBG] %s chat_id=%s user=%s text=%r", chat_kind, msg.chat.id, msg.from_user.id, text)
