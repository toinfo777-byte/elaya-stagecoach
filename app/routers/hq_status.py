# app/routers/hq_status.py
from __future__ import annotations

from aiogram import Router, types
from aiogram.filters import Command

from app.config import settings
from app.core.alerts import send_admin_alert

router = Router(name="hq_status")


@router.message(Command("panic"))
async def cmd_panic(message: types.Message):
    # Ничего не шлём в текущий чат; только в админ-канал через alerts
    title = "Webhook alert"
    body = (
        f"<code>env={settings.env} build={settings.build_mark}</code>\n"
        f"ValueError('Manual panic test: branch B')"
    )
    await send_admin_alert(
        bot=message.bot,
        title=title,
        body=body,
        tag="panic",
    )
    await message.answer("⚠️ Тест аварийного оповещения отправлен в админ-канал.")
