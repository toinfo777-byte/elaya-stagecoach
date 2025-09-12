# app/routers/debug.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import logging
log = logging.getLogger(__name__)

router = Router(name="debug")

@router.message()
async def debug_all_messages(m: Message):
    log.info("DBG message: chat=%s user=%s text=%r",
             m.chat.id, m.from_user.id if m.from_user else None, m.text)
    # ничего не отвечаем, просто логируем

@router.callback_query()
async def debug_all_callbacks(cq: CallbackQuery):
    log.info("DBG callback: chat=%s user=%s data=%r",
             cq.message.chat.id if cq.message else None,
             cq.from_user.id if cq.from_user else None,
             cq.data)
    # обязательно отвечаем на callback, чтобы «крутилка» не висела
    try:
        await cq.answer("ok")   # короткий ACK
    except Exception:
        pass
