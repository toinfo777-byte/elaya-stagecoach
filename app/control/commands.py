from __future__ import annotations

import logging

from aiogram import Router, F
from aiogram.types import Message

from app.control import PROCESS_STARTED_AT_MONO, ENV, RELEASE
from app.control.utils import (
    format_uptime,
    task_by_name,
    sentry_configured,
    cronitor_configured,
    admin_chat_ids,
)

# Если есть интеграция с observability.sentry — используем мягко
try:
    from app.observability.sentry import capture_test_message  # type: ignore
except Exception:  # pragma: no cover - нет модуля/функции
    capture_test_message = None  # type: ignore

router = Router(name="control")


# /status — сводка состояния
@router.message(F.text.in_({"/status", "status"}))
async def cmd_status(msg: Message) -> None:
    heartbeat = task_by_name("cronitor-heartbeat")
    uptime = format_uptime(PROCESS_STARTED_AT_MONO)

    sentry_ok = "🟢" if sentry_configured() else "⚪"
    cronitor_ok = "🟢" if cronitor_configured() else "⚪"
    hb_state = "🟢 running" if heartbeat and not heartbeat.done() else "⚪ idle"

    text = (
        "📟 <b>Bot status</b>\n"
        f"• Build: <code>{RELEASE}</code>\n"
        f"• Env: <code>{ENV}</code>\n"
        f"• Uptime: <code>{uptime}</code>\n"
        f"• Sentry: {sentry_ok}\n"
        f"• Cronitor: {cronitor_ok}\n"
        f"• Heartbeat task: <code>{hb_state}</code>\n"
    )
    await msg.answer(text)


# /reload — мягкая «перезагрузка» настроек (пока: ping Sentry + лог)
@router.message(F.text.in_({"/reload", "reload"}))
async def cmd_reload(msg: Message) -> None:
    logging.getLogger("control").info("reload requested via /reload")

    # Тестовый «пин» в Sentry, если он есть
    if capture_test_message:
        try:
            capture_test_message("🔁 control: soft reload requested")
        except Exception as e:
            logging.warning("Sentry capture_test_message failed: %s", e)

    await msg.answer("🔁 Мягкая перезагрузка выполнена (конфиг перечитан из ENV, если применимо).")


# /notify_admins — пробная рассылка администраторам
@router.message(F.text.in_({"/notify_admins", "notify_admins"}))
async def cmd_notify_admins(msg: Message) -> None:
    ids = admin_chat_ids()
    if not ids:
        await msg.answer("ℹ️ ADMIN_CHAT_IDS не задан — отправить некуда.")
        return

    sent = 0
    for chat_id in ids:
        try:
            await msg.bot.send_message(
                chat_id,
                f"📣 Admin notify: событие от <code>{RELEASE}</code> ({ENV})",
            )
            sent += 1
        except Exception as e:
            logging.warning("notify_admins: failed to send to %s: %s", chat_id, e)

    await msg.answer(f"📬 Отправлено администраторам: {sent}/{len(ids)}")
