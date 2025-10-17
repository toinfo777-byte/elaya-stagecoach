# app/routers/diag.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message
import json

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
    st = get_observe_status()
    pretty = json.dumps(st, ensure_ascii=False, indent=2)
    await msg.answer(f"🩺 <b>Diag</b>\n<pre>{pretty}</pre>")


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


@router.message(F.text.in_({"/heartbeat", "heartbeat"}))
async def cmd_heartbeat(msg: Message):
    await msg.answer("🩶 Всё живо. Элайя дышит.")
