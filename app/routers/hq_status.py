from __future__ import annotations

import os
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from app.config import settings
from app.core.status_utils import (
    build_hq_message,
    uptime_human,
    get_render_status,
)

router = Router(name="hq_status")


# /status — короткий пинг “ядро отвечает”
@router.message(Command("status"))
async def cmd_status(msg: Message) -> None:
    await msg.answer("🟢 HQ online: вебхук активен, ядро отвечает.")


# /webhookinfo — подробная сводка (env/build/uptime/Render)
@router.message(Command("webhookinfo"))
async def cmd_webhookinfo(msg: Message) -> None:
    text = build_hq_message()
    await msg.answer(text)


# /getme — ответ от Telegram API с данными бота
@router.message(Command("getme"))
async def cmd_getme(msg: Message) -> None:
    me = await msg.bot.get_me()
    await msg.answer(
        "\n".join(
            [
                "🤖 <b>getMe</b>",
                f"id=<code>{me.id}</code>",
                f"username=<code>{me.username}</code>",
                f"name=<code>{me.first_name}</code>",
            ]
        )
    )


# /panic — тест аварийной цепочки (Sentry + HQ alert)
@router.message(Command("panic"))
async def cmd_panic(msg: Message) -> None:
    await msg.answer("⚠️ Запускаю тест аварийного оповещения…")
    # намеренно бросаем исключение, которое поймает middleware/uvicorn
    raise ValueError("Manual panic test: branch B")


# /version — компактная версия/билд-отчёт
@router.message(Command("version"))
async def cmd_version(msg: Message) -> None:
    sha = settings.render_git_commit or settings.build_mark or "manual"
    sha_short = sha[:8]
    svc = settings.render_service or os.getenv("RENDER_SERVICE_NAME") or "—"
    inst = settings.render_instance or os.getenv("RENDER_INSTANCE_ID") or "—"
    region = settings.render_region or os.getenv("RENDER_REGION") or "—"

    lines = [
        "📦 <b>Version</b>",
        f"env=<code>{settings.env}</code>  mode=<code>{settings.mode}</code>",
        f"build=<code>{settings.build_mark}</code>  sha=<code>{sha_short}</code>",
        f"service=<code>{svc}</code>  instance=<code>{inst}</code>  region=<code>{region}</code>",
        f"uptime=<code>{uptime_human()}</code>",
    ]
    await msg.answer("\n".join(lines))


# /reboot — символическое подтверждение “перезапуска”
@router.message(Command("reboot"))
async def cmd_reboot(msg: Message) -> None:
    # Это не настоящий рестарт Render; мы фиксируем команду и шлём свежий снэпшот.
    await msg.answer("🔄 HQ restart acknowledged — обновляю сводку…")
    await msg.answer(build_hq_message())


# /render — краткий статус последнего билда Render (если настроен API)
@router.message(Command("render"))
async def cmd_render(msg: Message) -> None:
    report = await get_render_status()
    await msg.answer(report)
