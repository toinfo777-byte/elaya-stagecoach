from __future__ import annotations
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

import sentry_sdk

from app.observability.diag_status import get_observe_status
import os

router = Router(name="diag")

@router.message(Command("ping"))
async def cmd_ping(msg: Message):
    await msg.answer("pong 🟢")

@router.message(Command("health"))
async def cmd_health(msg: Message):
    await msg.answer("✅ Bot is alive and running!")

@router.message(Command("sentry_ping"))
async def cmd_sentry_ping(msg: Message):
    try:
        sentry_sdk.capture_message("✅ sentry: hello from elaya-stagecoach")
        await msg.answer("✅ Отправил тест-сообщение в Sentry")
    except Exception as e:
        await msg.answer(f"⚠️ Ошибка при отправке в Sentry: {e}")

@router.message(Command("boom"))
async def cmd_boom(msg: Message):
    await msg.answer("💣 Boom! Проверяем Sentry…")
    _ = 1 / 0  # намеренная ошибка

@router.message(Command("diag"))
async def cmd_diag(msg: Message):
    env = os.getenv("ENV", "develop").strip() or "develop"
    release = os.getenv("SHORT_SHA", "local").strip() or "local"
    st = get_observe_status(env=env, release=release)
    await msg.answer(
        "🔎 Диагностика\n"
        f"• env: <code>{st['env']}</code>\n"
        f"• release: <code>{st['release']}</code>\n"
        f"• render: <b>{st['render']}</b>\n"
        f"• bot: <b>{st['bot']}</b>\n"
        f"• sentry: <b>{st['sentry']}</b>\n"
        f"• cronitor: <b>{st['cronitor']}</b>\n"
    )
