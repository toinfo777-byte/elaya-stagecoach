from __future__ import annotations

from aiogram import Router, types
from aiogram.filters import Command

from app.config import settings
from app.status_utils import (
    build_hq_message,
    uptime_human,
    get_render_status,
)

router = Router(name="hq_status")


def _service_bits() -> str:
    bits: list[str] = []
    if settings.service_name:
        bits.append(f"service_name=`{settings.service_name}`")
    if settings.render_instance:
        bits.append(f"instance_id=`{settings.render_instance}`")
    if settings.render_git_commit:
        bits.append(f"sha=`{settings.render_git_commit[:8]}`")
    return " ".join(bits)


@router.message(Command("status"))
async def cmd_status(message: types.Message) -> None:
    """
    Краткая HQ-сводка — для ручной проверки в чатах/PM.
    """
    lines = [
        "🛰 <b>Штабной отчёт — Online</b>",
        f"<code>env={settings.env} build={settings.build_mark}</code>",
    ]
    sb = _service_bits()
    if sb:
        lines.append(sb)
    lines.append(f"uptime= `{uptime_human()}`")

    await message.answer("\n".join(lines))


@router.message(Command("version"))
async def cmd_version(message: types.Message) -> None:
    """
    Детали версии/окружения + последний билд Render (если токены заданы).
    """
    head = [
        "🧭 <b>Version / Env</b>",
        f"env=`{settings.env}` mode=`{settings.mode}` build=`{settings.build_mark}`",
    ]
    sb = _service_bits()
    if sb:
        head.append(sb)
    head.append(f"uptime=`{uptime_human()}`")

    render = await get_render_status()
    text = "\n".join(head) + "\n\n" + render
    await message.answer(text)


@router.message(Command("panic"))
async def cmd_panic(message: types.Message) -> None:
    """
    Тест аварийного оповещения в админ-чат.
    Отправляет 3 тестовых сообщения в ADMIN_ALERT_CHAT_ID.
    """
    admin_chat = settings.admin_alert_chat_id
    if not admin_chat:
        await message.answer("⚠️ ADMIN_ALERT_CHAT_ID не настроен — оповещение не отправлено.")
        return

    await message.answer("⚠️ Запускаю тест аварийного оповещения…")

    base = (
        "<b>Webhook alert</b>\n"
        f"env={settings.env} build={settings.build_mark}\n"
        "ValueError('Manual panic test: branch B')"
    )
    # Три коротких сообщения, как в примере
    for _ in range(3):
        try:
            await message.bot.send_message(admin_chat, base)
        except Exception as e:
            await message.answer(f"Не удалось отправить в ADMIN_ALERT_CHAT_ID: {e}")
            break


# Необязательная команда, чтобы посмотреть «полную» HQ-сводку из status_utils
@router.message(Command("hq"))
async def cmd_hq(message: types.Message) -> None:
    await message.answer(build_hq_message())
