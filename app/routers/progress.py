from __future__ import annotations
from aiogram import Router
from aiogram.types import Message, CallbackQuery

progress_router = Router(name="progress")

try:
    from app.storage.repo_extras import get_progress
except Exception:
    async def get_progress(user_id: int):
        return {"streak": 0, "episodes_7d": 0}


async def show_progress(obj: Message | CallbackQuery):
    user_id = obj.from_user.id if hasattr(obj, "from_user") else 0
    data = await get_progress(user_id)
    text = (
        "📈 Мой прогресс\n\n"
        f"• Стрик: {data.get('streak', 0)}\n"
        f"• Эпизодов за 7 дней: {data.get('episodes_7d', 0)}\n\n"
        "Продолжай каждый день — «Тренировка дня» в один клик 👇"
    )
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        await obj.message.answer(text)
    else:
        await obj.answer(text)
