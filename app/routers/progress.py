# app/routers/progress.py
from __future__ import annotations
from aiogram import Router
from aiogram.types import Message
from app.routers.menu import main_menu

router = Router(name="progress")

async def send_progress_card(m: Message):
    # здесь берёте реальные значения из БД
    streak = 35
    runs_7d = 35
    txt = (
        "📈 <b>Мой прогресс</b>\n\n"
        f"• Стрик: <b>{streak}</b>\n"
        f"• Этюдов за 7 дней: <b>{runs_7d}</b>\n\n"
        "Продолжай каждый день — тренировка дня в один клик 👇"
    )
    await m.answer(txt, reply_markup=main_menu())
