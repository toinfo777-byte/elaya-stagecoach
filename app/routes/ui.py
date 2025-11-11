# app/routes/ui.py
from __future__ import annotations
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from datetime import datetime
from app.core import store

router = APIRouter()

def _fmt_dt(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return iso

def _normalize_stats(raw: dict | None) -> dict:
    raw = raw or {}
    # поддерживаем оба формата
    users = raw.get("users", 0)
    last_updated = raw.get("last_updated") or raw.get("last_update")
    counts = raw.get("scene_counts") or raw.get("counts") or {}
    lr_obj = raw.get("last_reflection") or {}
    last_reflect = raw.get("last_reflect") or lr_obj.get("text")

    return {
        "users": int(users or 0),
        "last_updated": last_updated,
        "scene_counts": {
            "intro": int(counts.get("intro", 0) or 0),
            "reflect": int(counts.get("reflect", 0) or 0),
            "transition": int(counts.get("transition", 0) or 0),
        },
        "last_reflect": (last_reflect or "").strip() or "—",
    }

@router.get("/", response_class=HTMLResponse)
async def index():
    stats = _normalize_stats(store.get_stats())
    users = stats["users"]
    last_updated = _fmt_dt(stats["last_updated"])
    scenes = stats["scene_counts"]
    last_reflect = stats["last_reflect"]

    # простая палитра по умолчанию
    bg = "#0a0905"; fg = "#f7e8bb"; halo = "#fceaa7"; deep = "#d4b85a"
    name = "Elaya — School of Theatre of Light"
    motto = "Свет различает. Тьма хранит. Мы — между."

    return f"""
    <html>
      <head>
        <meta charset="utf-8"/>
        <title>{name}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <style>
          :root {{ --bg:{bg}; --fg:{fg}; --halo:{halo}; --deep:{deep}; }}
          * {{ box-sizing:border-box; }}
          html,body {{ height:100%; margin:0; }}
          body {{
            background: radial-gradient(60% 50% at 50% 35%, #111 0%, var(--bg) 60%, #000 100%);
            color: var(--fg); font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
            display:grid; place-items:center; padding:24px;
          }}
          .card {{ width:min(900px,92vw); background:rgba(10,9,5,.55); border:1px solid rgba(214,191,109,.25);
                  border-radius:20px; padding:28px 28px 22px; box-shadow:0 20px 60px rgba(0,0,0,.35); }}
          h1 {{ margin:0 0 6px; font-weight:800; letter-spacing:.04em; text-align:center; }}
          .motto {{ margin:0 0 18px; opacity:.85; text-align:center; }}
          .pulse {{ --size:22px; width:var(--size); height:var(--size); border-radius:50%; background:var(--fg);
                   box-shadow:0 0 10px var(--fg), 0 0 24px var(--halo), 0 0 48px rgba(255,230,170,.35);
                   margin:14px auto 8px; animation:breathe 3.6s ease-in-out infinite; }}
          @keyframes breathe {{ 0%{{transform:scale(.92);opacity:.88}} 50%{{transform:scale(1.06);opacity:1}}
                               100%{{transform:scale(.92);opacity:.88}} }}
          .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:14px; }}
          .tile {{ padding:14px 16px; border:1px solid rgba(214,191,109,.2); border-radius:14px; background:rgba(22,18,10,.35); }}
          .k {{ font-size:12px; letter-spacing:.12em; text-transform:uppercase; color:#cdbf8a; }}
          .v {{ font-weight:700; }}
          .muted {{ opacity:.75; }}
          .scenes {{ display:flex; gap:14px; margin-top:8px; flex-wrap:wrap; }}
          .badge {{ padding:6px 10px; border-radius:999px; border:1px solid rgba(214,191,109,.25); background:rgba(32,26,15,.35); font-weight:700; font-size:13px; }}
          .foot {{ margin-top:16px; padding-top:10px; border-top:1px dashed rgba(214,191,109,.25); font-size:13px; text-align:center; color:#d5c99e; }}
          .reflect {{ font-style:italic; line-height:1.55; }}
          @media (max-width:720px) {{ .grid {{ grid-template-columns:1fr; }} }}
        </style>
      </head>
      <body>
        <div class="card">
          <h1>{name}</h1>
          <p class="motto">{motto}</p>
          <div class="pulse" title="HQ Pulse — breathing"></div>

          <div class="grid">
            <div class="tile">
              <div class="k">Core · Состояние</div>
              <div class="v" style="margin-top:8px;">Пользователей в памяти: <span id="usersCnt">{users}</span></div>
              <div class="muted" style="margin-top:6px;">Последнее обновление: <span id="lastUpdated">{last_updated}</span></div>
              <div class="scenes" style="margin-top:8px;">
                <div class="badge">intro: <span id="introCnt">{scenes.get('intro',0)}</span></div>
                <div class="badge">reflect: <span id="reflectCnt">{scenes.get('reflect',0)}</span></div>
                <div class="badge">transition: <span id="transitionCnt">{scenes.get('transition',0)}</span></div>
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
              const r = await fetch('/ui/stats.json', {{cache:'no-store'}});
              const j = await r.json();
              const $ = (id,v)=>{{ const el=document.getElementById(id); if(el&&v!==undefined) el.textContent=v; }};

              const counts = j.counts || j.scene_counts || {{}};
              $('usersCnt', j.users ?? 0);
              $('introCnt', counts.intro ?? 0);
              $('reflectCnt', counts.reflect ?? 0);
              $('transitionCnt', counts.transition ?? 0);

              const lr = (j.last_reflection && j.last_reflection.text) ?? j.last_reflect ?? '—';
              $('lastReflection', (lr||'').trim() || '—');

              $('lastUpdated', j.last_update || j.last_updated || '—');
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
