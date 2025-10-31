from __future__ import annotations

import os
import time
from typing import Optional, Dict, List

from aiogram import Router, F
from aiogram.types import Message

import aiohttp

hq_router = Router(name="hq")

# Те же ENV-метки, что и в main.py
ENV = os.getenv("ENV", "staging")
MODE = os.getenv("MODE", "worker")
BUILD_MARK = os.getenv("BUILD_MARK", "manual")
RENDER_API_KEY = os.getenv("RENDER_API_KEY", "")
# Списки сервисов для /status_all
IDS_RAW = os.getenv("RENDER_SERVICE_ID", os.getenv("RENDER_SERVICE_IDS", ""))
LABELS_RAW = os.getenv("RENDER_SERVICE_LABELS", "")

START_TS = float(os.getenv("PROC_START_TS", str(time.time())))

RENDER_API_BASE = "https://api.render.com/v1"


# ─────────────────────────────
# Вспомогательный клиент Render
# ─────────────────────────────
class RenderClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

    async def _get(self, path: str, params: Optional[Dict] = None) -> Dict:
        url = f"{RENDER_API_BASE}{path}"
        async with aiohttp.ClientSession(headers=self.headers) as s:
            async with s.get(url, params=params) as r:
                r.raise_for_status()
                return await r.json()

    async def get_service(self, service_id: str) -> Dict:
        return await self._get(f"/services/{service_id}")

    async def get_last_deploy(self, service_id: str) -> Optional[Dict]:
        # /deploys возвращает список; берём последний
        data = await self._get(f"/services/{service_id}/deploys", params={"limit": 1})
        if isinstance(data, list) and data:
            return data[0]
        return None

    @staticmethod
    def load_ids_and_labels() -> List[Dict]:
        ids = [x.strip() for x in IDS_RAW.split(",") if x.strip()]
        labels = [x.strip() for x in LABELS_RAW.split(",")] if LABELS_RAW else []
        res: List[Dict] = []
        for i, sid in enumerate(ids):
            label = labels[i] if i < len(labels) else sid
            res.append({"id": sid, "label": label})
        return res


# ─────────────────────────────
# Базовые команды
# ─────────────────────────────
@hq_router.message(F.text == "/pong")
async def pong(m: Message):
    await m.answer("pong 🟢")


@hq_router.message(F.text == "/healthz")
async def healthz(m: Message):
    await m.answer("ok")


@hq_router.message(F.text == "/hq")
async def hq_summary(m: Message):
    # Здесь выводим «быструю сводку» по окружению — как у тебя в шаблоне
    sha = os.getenv("RENDER_GIT_COMMIT", "manual")
    uptime = int(time.time() - START_TS)
    service_id = os.getenv("RENDER_SERVICE_ID", "n/a")

    text = (
        "<b>🔧 HQ-сводка</b>\n"
        f"• Bot: ENV=<code>{ENV}</code> MODE=<code>{MODE}</code> BUILD=<code>{BUILD_MARK}</code>\n"
        f"• SHA=<code>{sha}</code>\n"
        f"• service_id=<code>{service_id}</code>\n"
        f"• Uptime: <code>{uptime//60}m {uptime%60}s</code>\n"
        "• Отчёт: не найден (проверьте daily/post-deploy отчёты)"
    )
    await m.answer(text)


# ─────────────────────────────
# /status_all — сводка по списку Render-сервисов
# ─────────────────────────────
@hq_router.message(F.text == "/status_all")
async def status_all(m: Message):
    if not RENDER_API_KEY:
        await m.answer("⚠️ Не задан RENDER_API_KEY.")
        return

    items = RenderClient.load_ids_and_labels()
    if not items:
        await m.answer("⚠️ Не задан список сервисов: RENDER_SERVICE_ID(S).")
        return

    client = RenderClient(RENDER_API_KEY)

    lines = ["<b>🧰 Render Services Status</b>"]
    for it in items:
        sid = it["id"]
        label = it["label"]
        try:
            svc = await client.get_service(sid)
            deploy = await client.get_last_deploy(sid)

            svc_suspended = bool(svc.get("service", {}).get("suspended", False))
            svc_status = "suspended" if svc_suspended else "active"

            if deploy:
                d_status = deploy.get("status", "—")
                d_branch = (deploy.get("commit") or {}).get("branch", "—")
                d_commit = (deploy.get("commit") or {}).get("id", "—")
                d_updated = deploy.get("updatedAt", "—")
            else:
                d_status = d_branch = d_commit = d_updated = "—"

            lines.append(
                f"\n• <b>{label}</b> <code>({sid})</code>\n"
                f"  ├─ service: <code>{svc_status}</code>\n"
                f"  ├─ deploy:  <code>{d_status}</code>\n"
                f"  ├─ branch:  <code>{d_branch}</code>\n"
                f"  ├─ commit:  <code>{d_commit}</code>\n"
                f"  └─ updated: <code>{d_updated}</code>"
            )
        except Exception as e:
            lines.append(f"\n• <b>{label}</b> <code>({sid})</code>\n  └─ error: <code>{e}</code>")

    await m.answer("\n".join(lines), parse_mode="HTML")
