# app/routes/ui.py
from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse
from app.core import store

router = APIRouter()


def _fmt_dt(ts: str | None) -> str:
    if not ts:
        return "—"
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ts


@router.get("/ui/stats.json")
async def ui_stats():
    """JSON-эндпоинт для автообновления панели"""
    return store.get_stats()


@router.get("/ui/ping")
async def ui_ping():
    """Проверка живости UI"""
    return Response(content="ui: ok", media_type="text/plain")


@router.get("/", response_class=HTMLResponse)
async def index():
    stats = store.get_stats()
    users = stats.get("users", 0)
    last_updated = _fmt_dt(stats.get("last_updated"))
    scenes = stats.get("scene_counts", {})
    last_reflect = stats.get("last_reflect") or "—"

    return f"""
    <html>
      <head>
        <meta charset="utf-8"/>
        <title>Elaya — School of Theatre of Light</title>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <style>
          :root {{
            --bg: #0a0905;
            --fg: #f7e8bb;
            --halo: #fceaa7;
            --deep: #d4b85a;
          }}
          * {{ box-sizing: border-box; }}
          html, body {{ height: 100%; margin: 0; }}
          body {{
            background: radial-gradient(60% 50% at 50% 35%, #111 0%, var(--bg) 60%, #000 100%);
            color: var(--fg);
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
            display: grid;
            place-items: center;
            padding: 24px;
          }}
          .card {{
            width: min(900px, 92vw);
            background: rgba(10, 9, 5, .55);
            border: 1px solid rgba(214, 191, 109, .25);
            border-radius: 20px;
            padding: 28px 28px 22px;
            box-shadow: 0 20px 60px rgba(0,0,0,.35);
          }}
          h1 {{ margin: 0 0 6px; font-weight: 800; letter-spacing: .04em; text-align: center; }}
          .motto {{ margin: 0 0 18px; opacity: .85; text-align: center; }}
          .pulse {{
            --size: 22px; width: var(--size); height: var(--size); border-radius: 50%;
            background: var(--fg);
            box-shadow: 0 0 10px var(--fg), 0 0 24px var(--halo), 0 0 48px rgba(255,230,170,.35);
            margin: 14px auto 8px; animation: breathe 3.6s ease-in-out infinite;
          }}
          @keyframes breathe {{ 0%{{transform:scale(.92);opacity:.88}} 50%{{transform:scale(1.06);opacity:1}} 100%{{transform:scale(.92);opacity:.88}} }}
          .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px; }}
          .tile {{ padding: 14px 16px; border: 1px solid rgba(214,191,109,.2); border-radius: 14px; background: rgba(22,18,10,.35); }}
          .k {{ font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: #cdbf8a; }}
          .v {{ font-weight: 700; }}
          .muted {{ opacity: .75; }}
          .scenes {{ display: flex; gap: 14px; margin-top: 8px; flex-wrap: wrap; }}
          .badge {{ padding: 6px 10px; border-radius: 999px; border: 1px solid rgba(214,191,109,.25); background: rgba(32,26,15,.35); font-weight: 700; font-size: 13px; }}
          .foot {{ margin-top: 16px; padding-top: 10px; border-top: 1px dashed rgba(214,191,109,.25); font-size: 13px; text-align: center; color: #d5c99e; }}
          .reflect {{ font-style: italic; line-height: 1.55; }}
          @media (max-width: 720px) {{ .grid {{ grid-template-columns: 1fr; }} }}
        </style>
      </head>
      <body>
        <div class="card">
          <h1>Elaya — School of Theatre of Light</h1>
          <p class="motto">Свет различает. Тьма хранит. Мы — между.</p>
          <div class="pulse" title="HQ Pulse — breathing"></div>

          <div class="grid">
            <div class="tile">
              <div class="k">Core · Состояние</div>
              <div class="v" style="margin-top:8px;">Пользователей в памяти: <span id="usersCnt">{users}</span></div>
              <div class="muted" style="margin-top:6px;">Последнее обновление: <span id="lastUpdated">{last_updated}</span></div>
              <div class="scenes">
                <div class="badge">intro: <span id="introCnt">{scenes.get('intro', 0)}</span></div>
                <div class="badge">reflect: <span id="reflectCnt">{scenes.get('reflect', 0)}</span></div>
                <div class="badge">transition: <span id="transitionCnt">{scenes.get('transition', 0)}</span></div>
              </div>
            </div>
            <div class="tile">
              <div class="k">Reflection · Последняя заметка</div>
              <div id="lastReflection" class="reflect" style="margin-top:8px;">{last_reflect}</div>
            </div>
          </div>

          <div class="foot">HQ Panel · Cycle Active · Memory Stable · Reflection On</div>
        </div>

        <script>
        async function refreshStats(){{
          try {{
            const r = await fetch('/ui/stats.json', {{ cache: 'no-store' }});
            const j = await r.json();

            // совместимость ключей: новая и старая схемы
            const counts = j.counts || j.scene_counts || {{}};
            const lastUpdate = j.last_update || j.last_updated || '—';
            const lastReflection = (j.last_reflection && j.last_reflection.text) || j.last_reflect || '—';

            const $ = (id, v) => {{ const el = document.getElementById(id); if (el && v !== undefined) el.textContent = v; }};

            $('usersCnt', j.users ?? 0);
            $('introCnt', counts.intro ?? 0);
            $('reflectCnt', counts.reflect ?? 0);
            $('transitionCnt', counts.transition ?? 0);
            $('lastUpdated', lastUpdate || '—');
            $('lastReflection', (lastReflection && String(lastReflection).trim()) ? lastReflection : '—');
          }} catch(e) {{
            console.warn('stats refresh failed', e);
          }}
        }}
        refreshStats();
        setInterval(refreshStats, 8000);
        </script>
      </body>
    </html>
    """
