# app/utils/tg_safe.py
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message

async def safe_answer(cb: CallbackQuery, text: str | None = None, show_alert: bool = False) -> None:
    """
    Безопасно отвечает на callback. Игнорирует 'query is too old' и подобные.
    """
    try:
        await cb.answer(text or "", show_alert=show_alert)
    except TelegramBadRequest as e:
        # самые частые «невредные» кейсы
        s = str(e).lower()
        if "query is too old" in s or "invalid" in s:
            return
        raise

async def safe_edit_text(msg: Message, text: str, **kwargs) -> Message | None:
    """
    Безопасно редактирует текст сообщения. Игнорирует 'message is not modified'
    и ситуации, когда сообщение уже нельзя редактировать.
    """
    try:
        return await msg.edit_text(text, **kwargs)
    except TelegramBadRequest as e:
        s = str(e).lower()
        if "not modified" in s or "message to edit not found" in s or "message can't be edited" in s:
            return None
        raise

async def safe_edit_reply_markup(msg: Message, **kwargs) -> Message | None:
    try:
        return await msg.edit_reply_markup(**kwargs)
    except TelegramBadRequest as e:
        s = str(e).lower()
        if "message to edit not found" in s or "message is not modified" in s:
            return None
        raise
