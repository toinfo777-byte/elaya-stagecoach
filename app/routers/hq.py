from __future__ import annotations
import os
import textwrap
from datetime import datetime, timezone

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="hq")

ALLOWED_CHATS = {"private", "group", "supergroup"}

def _render_services() -> list[tuple[str, str]]:
    ids = os.getenv("RENDER_SERVICE_ID", "")
    labels = os.getenv("RENDER_SERVICE_LABELS", "")
    id_list = [s.strip() for s in ids.split(",") if s.strip()]
    label_list = [s.strip() for s in labels.split(",") if s.strip()]
    out = []
    for i, sid in enumerate(id_list):
        lbl = label_list[i] if i < len(label_list) else f"service-{i+1}"
        out.append((lbl, sid))
    return out

# --- базовые пинги (работают в приватах и группах) ---
@router.message(Command(commands={"ping"}) & F.chat.type.in_(ALLOWED_CHATS))
async def cmd_ping(msg: Message):
    await msg.reply("pong 🟢")

@router.message(Command(commands={"healthz"}) & F.chat.type.in_(ALLOWED_CHATS))
async def cmd_healthz(msg: Message):
    await msg.reply("ok ✅")

# --- HQ краткая сводка ---
@router.message(Command(commands={"hq"}) & F.chat.type.in_(ALLOWED_CHATS))
async def cmd_hq(msg: Message):
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

# --- /status (без настоящего Render API пока) ---
@router.message(Command(commands={"status"}) & F.chat.type.in_(ALLOWED_CHATS))
async def cmd_status(msg: Message):
    api_key = os.getenv("RENDER_API_KEY", "")
    if not api_key:
        await msg.reply("⚠️ Не настроены RENDER_API_KEY и RENDER_SERVICE_ID.")
        await msg.reply(textwrap.dedent("""\
            <b>Render Build</b>
            Branch: –
            Commit: –
            Status: –
            Created: –
            Updated: –
        """))
        return
    await msg.reply("🔧 API-ключ есть, но клиент ещё не подключён.")
