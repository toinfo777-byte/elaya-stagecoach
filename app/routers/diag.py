from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message
import sentry_sdk

from app.observability.diag_status import get_observe_status

router = Router(name="diag")


@router.message(F.text.in_({"/ping", "ping"}))
async def cmd_ping(msg: Message):
    await msg.answer("pong 🟢")


@router.message(F.text.in_({"/health", "health"}))
async def cmd_health(msg: Message):
    await msg.answer("✅ Bot is alive and running!")


@router.message(F.text.in_({"/diag", "diag"}))
async def cmd_diag(msg: Message):
    status = get_observe_status()
    pretty = "\n".join(f"• {k}: {v}" for k, v in status.items())
    await msg.answer(f"🩺 <b>Observe</b>\n{pretty}")


@router.message(F.text.in_({"/sentry_ping", "sentry_ping"}))
async def cmd_sentry_ping(msg: Message):
    try:
        sentry_sdk.capture_message("✅ sentry: hello from elaya-stagecoach")
        await msg.answer("✅ Отправил тест-сообщение в Sentry")
    except Exception as e:
        await msg.answer(f"⚠️ Ошибка при отправке в Sentry: {e}")


@router.message(F.text.in_({"/boom", "boom"}))
async def cmd_boom(msg: Message):
    await msg.answer("💣 Boom! Проверяем Sentry…")
    _ = 1 / 0  # намеренная ошибка
