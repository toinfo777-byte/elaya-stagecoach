# app/routes/ui.py
from __future__ import annotations

import os
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

MOTTO = "Свет различает. Тьма хранит. Мы — между."
PALETTE = {
    "bg": "#0b1020",
    "card": "#121a33",
    "accent": "#3aa3ff",
    "ok": "#38d996",
    "muted": "#9fb3c8",
}

def meta():
    return {
        "identity": os.getenv("BOT_PROFILE", "hq"),
        "env": os.getenv("ENV", "staging"),
        "build": os.getenv("BUILD_MARK", "manual"),
        "year": "2025",
    }

@router.get("/", response_class=HTMLResponse)
def root() -> str:
    m = meta()
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Elaya HQ · {m['identity']}</title>
  <style>
    :root {{
      --bg: {PALETTE['bg']};
      --card: {PALETTE['card']};
      --accent: {PALETTE['accent']};
      --ok: {PALETTE['ok']};
      --muted: {PALETTE['muted']};
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; min-height: 100vh; display: grid; place-items: center;
      background: radial-gradient(60% 60% at 50% 40%, rgba(58,163,255,.15), transparent 60%), var(--bg);
      color: #eef3ff; font: 16px/1.6 ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Noto Sans";
    }}
    .card {{
      width: min(860px, 92vw);
      background: linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.02));
      border: 1px solid rgba(255,255,255,.06);
      border-radius: 16px; padding: 28px 28px 22px; box-shadow: 0 10px 40px rgba(0,0,0,.35);
      backdrop-filter: blur(6px);
    }}
    h1 {{ margin: 0 0 6px; font-weight: 700; letter-spacing: .2px; }}
    .motto {{ margin: 2px 0 14px; color: var(--muted); font-weight: 500; }}
    .row {{ display: flex; flex-wrap: wrap; gap: 10px; color:#cfe2ff; }}
    .tag {{
      padding: 6px 10px; border-radius: 999px;
      background: rgba(58,163,255,.14); border: 1px solid rgba(58,163,255,.2); color:#e7f2ff;
      font-size: 13px;
    }}
    .ok {{ background: rgba(56,217,150,.12); border-color: rgba(56,217,150,.28); color:#eafff6; }}
    footer {{ margin-top: 14px; color: #91a7c3; font-size: 12px; }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <main class="card">
    <h1>Elaya StageCoach · HQ</h1>
    <div class="motto">{MOTTO}</div>
    <div class="row">
      <span class="tag">profile: <b>{m['identity']}</b></span>
      <span class="tag">env: <b>{m['env']}</b></span>
      <span class="tag">build: <b>{m['build']}</b></span>
      <span class="tag ok">health: OK</span>
    </div>
    <footer>
      • Диагностика: <a href="/diag/ping">/diag/ping</a>,
      <a href="/diag/webhook">/diag/webhook</a>,
      <a href="/diag/status_json">/diag/status_json</a><br/>
      • © Elaya {m['year']}
    </footer>
  </main>
</body>
</html>"""
