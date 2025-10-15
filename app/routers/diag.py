from aiogram import Router, F
from aiogram.types import Message
import sentry_sdk

router = Router(name="diag")

# ... твои /ping, /sentry_ping, /boom остаются ...

@router.message(F.text.in_({"/sentry_status", "sentry_status"}))
async def cmd_sentry_status(msg: Message):
    hub = sentry_sdk.Hub.current
    client = getattr(hub, "client", None)
    if not client:
        await msg.answer("⚠️ Sentry: клиент не инициализирован")
        return
    opts = getattr(client, "options", {}) or {}
    dsn = str(opts.get("dsn") or "")
    env = opts.get("environment")
    rel = opts.get("release")
    await msg.answer(
        "🧭 Sentry статус:\n"
        f"• initialized: ✅\n"
        f"• env: {env}\n"
        f"• release: {rel}\n"
        f"• dsn set: {'yes' if dsn else 'no'}"
    )

@router.message(F.text.in_({"/sentry_force", "sentry_force"}))
async def cmd_sentry_force(msg: Message):
    try:
        sentry_sdk.capture_message("🧪 forced test message (manual)")
        sentry_sdk.flush(timeout=5.0)  # дождаться отправки
        await msg.answer("✅ Отправил и флэшнул событие в Sentry")
    except Exception as e:
        await msg.answer(f"⚠️ Ошибка при отправке/flush: {e}")
