# app/routers/debug.py
import logging
from aiogram import Router
from aiogram.types import Message, CallbackQuery

router = Router(name="debug")
log = logging.getLogger("debug")

# Логируем любое входящее сообщение (не мешаем остальным хендлерам)
@router.message()
async def _debug_any_message(m: Message) -> None:
    log.info("MSG: from=%s chat=%s text=%r", m.from_user.id if m.from_user else None, m.chat.id, m.text)

# Логируем любые callback’и (клики по инлайн-клавиатуре)
@router.callback_query()
async def _debug_any_callback(c: CallbackQuery) -> None:
    log.info("CB:  from=%s chat=%s data=%r", c.from_user.id if c.from_user else None, c.message.chat.id if c.message else None, c.data)
    # отвечаем коротко, чтобы Telegram убирал «часики»
    try:
        await c.answer(cache_time=0)
    except Exception as e:
        log.warning("Callback answer failed: %s", e)
