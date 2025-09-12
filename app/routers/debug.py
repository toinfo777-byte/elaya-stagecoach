# app/routers/debug.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

router = Router()
router.name = "debug"

@router.message()
async def any_message(m: Message):
    # ничему не мешаем — просто лог для диагностики
    text = (m.text or "").strip()
    m.bot.logger.info("DBG MSG from %s: %r", m.from_user.id if m.from_user else "?", text)

@router.callback_query()
async def any_callback(cb: CallbackQuery):
    data = (cb.data or "").strip()
    cb.bot.logger.info("DBG CB from %s: %r", cb.from_user.id if cb.from_user else "?", data)
    # обязательно отвечаем, чтобы Telegram убирал «часики»
    try:
        await cb.answer()
    except Exception:
        pass
