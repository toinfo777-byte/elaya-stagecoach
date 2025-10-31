from __future__ import annotations
import json
import os
import textwrap
from datetime import datetime, timezone

from aiogram import Router, types, F
from aiogram.filters import Command

router = Router(name="hq")

def _render_services() -> list[tuple[str, str]]:
    # ENV переменные ты уже заполнил на Render
    ids = os.getenv("RENDER_SERVICE_ID", "")
    labels = os.getenv("RENDER_SERVICE_LABELS", "")
    id_list = [s.strip() for s in ids.split(",") if s.strip()]
    label_list = [s.strip() for s in labels.split(",") if s.strip()]
    out = []
    for i, sid in enumerate(id_list):
        lbl = label_list[i] if i < len(label_list) else f"service-{i+1}"
        out.append((lbl, sid))
    return out

@router.message(Command("ping"))
async def cmd_ping(msg: types.Message):
    await msg.reply("pong 🟢")

@router.message(Command("healthz"))
async def cmd_healthz(msg: types.Message):
    await msg.reply("ok ✅")

@router.message(Command("hq"))
async def cmd_hq(msg: types.Message):
    """
    Короткая тех. сводка по Render-сервисам (по ENV).
    """
    services = _render_services()
    now = datetime.now(timezone.utc).astimezone()
    lines = [
        "🛰 <b>Штабные отчёты</b>",
        f"<i>{now:%Y-%m-%d %H:%M:%S %Z}</i>",
        "",
        "• <b>Render Build</b>",
        "  Branch: –",
        "  Commit: –",
        "  Status: –",
        "  Created: –",
        "  Updated: –",
        "",
        "• <b>Services</b>",
    ]
    if services:
        for lbl, sid in services:
            lines.append(f"  — {lbl}: <code>{sid}</code>")
    else:
        lines.append("  — (не настроены RENDER_SERVICE_ID / RENDER_SERVICE_LABELS)")

    await msg.reply("\n".join(lines))

@router.message(Command("status"))
async def cmd_status(msg: types.Message):
    """
    Плейсхолдер под будущий REST-опрос Render API (когда добавим ключ и клиент).
    Пока просто отображаем, что ключей нет — чтобы сообщение в группе было читабельным.
    """
    api_key = os.getenv("RENDER_API_KEY", "")
    if not api_key:
        await msg.reply("⚠️ Не настроены RENDER_API_KEY и RENDER_SERVICE_ID.")
        # и всё равно отдаём аккуратный блок:
        await msg.reply(
            textwrap.dedent(
                """\
                <b>Render Build</b>
                Branch: –
                Commit: –
                Status: –
                Created: –
                Updated: –
                """
            )
        )
        return

    # Если добавишь клиент — здесь можно будет реально ходить в Render API.
    await msg.reply("🔧 API-ключ есть, но клиент ещё не подключён.")
