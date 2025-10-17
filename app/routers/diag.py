# app/routers/diag.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message

from app.sentry import SENTRY_OK, capture_message, capture_exception

router = Router(name="diag")


@router.message(F.text.in_({"/ping", "ping"}))
async def cmd_ping(msg: Message):
    await msg.answer("pong 🟢")


@router.message(F.text.in_({"/health", "health"}))
async def cmd_health(msg: Message):
    await msg.answer("✅ Bot is alive and running!")


@router.message(F.text.in_({"/sentry_ping", "sentry_ping"}))
async def cmd_sentry_ping(msg: Message):
    # Явно шлём сообщение в Sentry с полезными тегами.
    capture_message(
        "✅ sentry: hello from elaya-stagecoach",
        tags={
            "route": "/sentry_ping",
            "chat_id": msg.chat.id,
            "user_id": msg.from_user.id if msg.from_user else "unknown",
        },
    )
    if SENTRY_OK:
        await msg.answer("✅ Отправил тест-сообщение в Sentry")
    else:
        await msg.answer("⚠️ Sentry сейчас выключен (нет DSN)")


@router.message(F.text.in_({"/boom", "boom"}))
async def cmd_boom(msg: Message):
    await msg.answer("💣 Boom! Проверяем Sentry…")
    try:
        _ = 1 / 0  # намеренная ошибка
    except Exception as e:
        # Явно репортим исключение в Sentry с тегами и пробрасываем дальше,
        # чтобы не скрывать поведение.
        capture_exception(
            e,
            tags={
                "route": "/boom",
                "chat_id": msg.chat.id,
                "user_id": msg.from_user.id if msg.from_user else "unknown",
            },
        )
        # пробрасывать не обязательно; оставим логикой soft-fail
        # raise
