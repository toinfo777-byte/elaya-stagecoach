# app/routes/ui.py
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime

router = APIRouter()


# --- API: ping & stats -------------------------------------------------------

@router.get("/ui/ping")
async def ui_ping():
    return {"ui": "ok"}


def _stats_payload() -> dict:
    # Здесь можно подставить реальные значения из БД/кеша, если появятся
    return {
        "core": {
            "users": 0,
            "intro": 0,
            "reflect": 0,
            "transition": 0,
            "last_updated": "",
        },
        "reflection": {"text": "", "updated_at": ""},
        "status": "ok",
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


@router.get("/ui/stats.json")
async def ui_stats():
    return JSONResponse(_stats_payload())


# --- UI: главная панель ------------------------------------------------------

_PAGE_HTML = r"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Элайя — StageCoach • Панель</title>
  <style>
    :root {
      --bg: #0c0f14;
      --panel: #151a22;
      --text: #e9ecf1;
      --muted: #9aa3af;
      --chip: #1f2631;
      --glow: #ffeb99;
      --accent: #ffd76a;
      --ok: #22c55e;
    }
    * { box-sizing: border-box; }
    html, body { height: 100%; }
    body {
      margin: 0; background: radial-gradient(1000px 400px at 30% 0%, #131822 0%, var(--bg) 60%);
      color: var(--text); font: 16px/1.45 system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, "Helvetica Neue", Arial, "Noto Sans", "Apple Color Emoji", "Segoe UI Emoji";
    }
    .wrap { max-width: 1100px; margin: 48px auto; padding: 0 20px; }
    h1 { font-size: 48px; margin: 0 0 8px; letter-spacing: .5px; }
    .dot { display:inline-block; width: 12px; height: 12px; margin-left: 10px; border-radius: 999px; background: var(--accent);
           box-shadow: 0 0 18px var(--glow), 0 0 42px var(--glow); vertical-align: middle; }
    .subtitle { color: var(--muted); margin-bottom: 24px; }
    .grid { display: grid; gap: 18px; grid-template-columns: 1fr 1fr; }
    .card { background: linear-gradient(180deg, rgba(255,255,255,.02), rgba(0,0,0,.05)), var(--panel);
            border-radius: 18px; padding: 20px; box-shadow: 0 8px 24px rgba(0,0,0,.35) inset, 0 1px 0 rgba(255,255,255,.04); }
    .card h3 { margin: 0 0 14px; font-size: 14px; letter-spacing: .12em; color: var(--muted); text-transform: uppercase; }
    .chips { display:flex; flex-wrap:wrap; gap:10px; }
    .chip { background: var(--chip); border-radius: 999px; padding: 8px 12px; color: var(--text); display:inline-flex; gap:8px; align-items:center; }
    .chip.ok::before { content:""; width:8px; height:8px; background: var(--ok); border-radius: 999px; box-shadow: 0 0 8px rgba(34,197,94,.7); }
    .badge { background:#0f1420; border:1px solid #2a3443; border-radius:999px; padding: 6px 10px; color:#cdd5df; }
    .muted { color: var(--muted); }
    .kpi-row { display:flex; gap:12px; flex-wrap:wrap; }
    .kpi { background: var(--chip); padding:10px 12px; border-radius: 12px; }
    .footer { display:flex; gap:10px; flex-wrap:wrap; margin-top: 16px; }
    .lamp { width: 12px; height: 12px; border-radius: 999px; background: var(--accent); box-shadow: 0 0 14px var(--glow); }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
    @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Элайя — StageCoach <span class="dot"></span></h1>
    <div class="subtitle">панель наблюдения</div>

    <div class="grid">
      <div class="card">
        <h3>Портал</h3>
        <div class="chips">
          <span class="badge">Stable</span>
          <span class="badge">Online</span>
          <span class="badge">Light active</span>
        </div>

        <div class="footer">
          <span class="chip">• HQ Panel</span>
          <span class="chip ok">• Cycle Active</span>
          <span class="chip">• Memory Stable</span>
          <span class="chip">• Reflection On</span>
        </div>
      </div>

      <div class="card">
        <h3>Последняя заметка · Reflection</h3>
        <div id="reflectionText" class="muted">—</div>
        <div style="display:flex; align-items:center; gap:10px; margin-top:12px;">
          <div class="lamp"></div>
          <div id="reflectionTime" class="muted mono">—</div>
        </div>
        <div style="margin-top:10px;" class="muted mono" id="ts">—</div>
      </div>
    </div>

    <div class="card" style="margin-top:18px;">
      <h3>Core · Состояние</h3>
      <div class="muted">Последнее обновление ядра: <span id="lastUpdated">—</span></div>
      <div class="kpi-row" style="margin-top:10px;">
        <div class="kpi mono">intro: <span id="kIntro">0</span></div>
        <div class="kpi mono">reflect: <span id="kReflect">0</span></div>
        <div class="kpi mono">transition: <span id="kTransition">0</span></div>
      </div>
      <div class="footer">
        <span class="chip">• HQ Panel</span>
        <span class="chip ok">• Cycle Active</span>
        <span class="chip">• Memory Stable</span>
        <span class="chip">• Reflection On</span>
      </div>
    </div>
  </div>

  <script>
    const $ = (id) => document.getElementById(id);

    async function pull() {
      try {
        const r = await fetch('/ui/stats.json', { cache: 'no-store' });
        if (!r.ok) throw new Error('HTTP ' + r.status);
        const data = await r.json();

        // timestamps
        $('ts').textContent = data.ts || '—';

        // reflection
        $('reflectionText').textContent = (data.reflection && data.reflection.text) ? data.reflection.text : '—';
        $('reflectionTime').textContent = (data.reflection && data.reflection.updated_at) ? data.reflection.updated_at : '—';

        // core
        const core = data.core || {};
        $('lastUpdated').textContent = core.last_updated || '—';
        $('kIntro').textContent = core.intro ?? 0;
        $('kReflect').textContent = core.reflect ?? 0;
        $('kTransition').textContent = core.transition ?? 0;
      } catch (e) {
        console.warn('ui refresh failed:', e);
      }
    }

    pull();
    setInterval(pull, 10000);
  </script>
</body>
</html>
"""

@router.get("/", response_class=HTMLResponse)
async def ui_index():
    return HTMLResponse(_PAGE_HTML)
