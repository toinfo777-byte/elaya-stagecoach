# app/routes/ui.py
from __future__ import annotations

import html
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Body, Form, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse

from app.core import store
from app.core.meta import meta  # если нет meta.py – можно закомментировать эти 2 строки и ниже заменить meta.*
# meta.name / meta.motto / meta.palette используются для цветов и заголовков

router = APIRouter()

# ---------- helpers ----------

def _fmt_dt(iso: Optional[str]) -> str:
    if not iso:
        return "—"
    try:
        # ожидаем ISO с 'Z' или смещением
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return iso

def _ui_stats_payload() -> dict[str, Any]:
    """
    Унифицируем JSON для фронта:
    {
      "ok": True,
      "core": {"users": int, "intro": int, "reflect": int, "transition": int, "last_updated": str},
      "reflection": {"text": str|None, "updated_at": str|None}
    }
    """
    # стараемся брать расширенную сводку, затем – компактную
    core_counts = {"users": 0, "intro": 0, "reflect": 0, "transition": 0, "last_updated": ""}
    reflection = {"text": None, "updated_at": None}

    try:
        # расширенная (есть в твоём store.py)
        s = store.get_stats()  # users, last_update, counts{...}, last_reflection{text,at}
        if s:
            c = s.get("counts", {}) or {}
            core_counts = {
                "users": int(s.get("users") or 0),
                "intro": int(c.get("intro") or 0),
                "reflect": int(c.get("reflect") or 0),
                "transition": int(c.get("transition") or 0),
                "last_updated": s.get("last_update") or "",
            }
            lr = s.get("last_reflection") or {}
            reflection = {
                "text": lr.get("text"),
                "updated_at": lr.get("at"),
            }
    except Exception:
        # fallback: компактная
        try:
            cs = store.get_scene_stats()  # counts{...}, last_updated, last_reflection
            if cs:
                counts = cs.get("counts", {}) or {}
                core_counts.update({
                    "intro": int(counts.get("intro") or 0),
                    "reflect": int(counts.get("reflect") or 0),
                    "transition": int(counts.get("transition") or 0),
                    "last_updated": cs.get("last_updated") or "",
                })
                # users в compact нет — попробуем получить отдельно
                try:
                    # грубо, но ок для UI
                    users = store.get_counts()["users"]  # если функция есть
                    core_counts["users"] = int(users or 0)
                except Exception:
                    pass
                reflection = {
                    "text": cs.get("last_reflection"),
                    "updated_at": cs.get("last_updated"),
                }
        except Exception:
            pass

    return {
        "ok": True,
        "core": core_counts,
        "reflection": reflection,
    }

# ---------- routes ----------

@router.get("/ui/ping")
async def ui_ping() -> Response:
    return PlainTextResponse('{"ui":"ok"}', media_type="application/json")

@router.get("/ui/stats.json")
async def ui_stats() -> JSONResponse:
    return JSONResponse(_ui_stats_payload())

@router.post("/ui/reflection/save")
async def ui_reflection_save(
    # принимаем И JSON, И form-data
    text_json: Optional[str] = Body(None, embed=True),
    text_form: Optional[str] = Form(None),
) -> JSONResponse:
    text = (text_json if (text_json is not None) else text_form) or ""
    text = text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="empty")

    # Для панели HQ нет реального user_id — пишем в «системного» пользователя 1
    user_id = 1
    try:
        # гарантируем, что строка существует
        store.upsert_scene(user_id, last_scene="reflect", last_reflect=text)
        # и отдельно дёрнем add_reflection (обновит updated_at на более свежий момент)
        store.add_reflection(user_id, text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"save failed: {e}")

    return JSONResponse({"ok": True})

@router.get("/", response_class=HTMLResponse)
async def index(_: Request) -> HTMLResponse:
    # палитра/имена (если meta отсутствует — подставь дефолты)
    try:
        colors = meta.palette or {}
        name = meta.name or "Elaya — School of Theatre of Light"
        motto = meta.motto or "Свет различает. Тьма хранит. Мы — между."
    except Exception:
        colors = {}
        name = "Elaya — StageCoach"
        motto = "Свет различает. Тьма хранит. Мы — между."

    bg = colors.get("dark_core", "#0a0905")
    fg = colors.get("core_light", "#f7e8bb")
    halo = colors.get("halo_gold", "#fceaa7")
    deep = colors.get("deep_gold", "#d4b85a")

    # статический каркас; данные подтягиваем через /ui/stats.json
    html_page = f"""
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{html.escape(name)} · HQ Panel</title>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <style>
    :root {{
      --bg: {bg};
      --fg: {fg};
      --halo: {halo};
      --deep: {deep};
      --panel: rgba(10, 9, 5, .55);
      --panel-border: rgba(214, 191, 109, .25);
      --radius-xl: 20px;
      --radius: 12px;
      --soft-shadow: 0 20px 60px rgba(0,0,0,.35);
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
    .hq-container {{ width: min(1000px, 92vw); }}
    .hq-title {{ margin: 0 0 6px; font-weight: 800; letter-spacing: .04em; text-align: center; }}
    .hq-subtitle {{ margin: 0 0 18px; opacity: .85; text-align: center; }}

    .pulse {{
      --size: 22px;
      width: var(--size); height: var(--size); border-radius: 50%;
      background: var(--fg);
      box-shadow: 0 0 10px var(--fg), 0 0 24px var(--halo), 0 0 48px rgba(255,230,170,.35);
      display: inline-block; margin-left: 10px; vertical-align: middle;
      animation: breathe 3.6s ease-in-out infinite;
    }}
    @keyframes breathe {{
      0% {{ transform: scale(0.92); opacity: .88; }}
      50% {{ transform: scale(1.06); opacity: 1;   }}
      100% {{ transform: scale(0.92); opacity: .88; }}
    }}

    .hq-panel {{ background: var(--panel); border: 1px solid var(--panel-border); border-radius: var(--radius-xl); padding: 22px; box-shadow: var(--soft-shadow); }}
    .hq-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    .card {{ padding: 16px; border: 1px solid rgba(214, 191, 109, .2); border-radius: 14px; background: rgba(22,18,10,.35); }}
    .stripe {{ height: 1px; margin-bottom: 12px; background: linear-gradient(90deg, transparent, var(--halo), transparent); }}
    .pills {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .pill {{ padding: 6px 10px; border-radius: 999px; border: 1px solid rgba(214,191,109,.25); background: rgba(32,26,15,.35); font-weight: 700; font-size: 13px; }}
    .pill--intro {{ }}
    .pill--reflect {{ }}
    .pill--transition {{ }}

    .reflect-box .reflect-text {{ font-style: italic; line-height: 1.55; min-height: 64px; }}
    .reflect-footer {{ display: flex; align-items: center; justify-content: space-between; opacity: .85; }}

    .badge {{ display: inline-flex; align-items: center; gap: 6px; padding: 6px 10px; border-radius: 999px; border: 1px solid rgba(214,191,109,.25); background: rgba(32,26,15,.35); font-weight: 700; font-size: 12px; }}
    .badge .dot {{ width: 8px; height: 8px; border-radius: 999px; display: inline-block; background: var(--fg); opacity: .9; }}

    .hq-status {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-top: 10px; }}
    .btn {{
      appearance: none; border: 1px solid rgba(214,191,109,.35); background: rgba(32,26,15,.5); color: var(--fg);
      border-radius: 10px; padding: 8px 12px; font-weight: 700; cursor: pointer;
    }}
    .btn:hover {{ background: rgba(32,26,15,.7); }}

    /* modal */
    #noteModal {{
      display:none; position:fixed; inset:0; background:rgba(0,0,0,.5);
      align-items:center; justify-content:center; z-index:1000;
    }}
    #noteModal .box {{
      width: min(680px, 92vw); background: var(--panel); border: 1px solid var(--panel-border);
      border-radius: var(--radius-xl); padding: 18px; box-shadow: var(--soft-shadow);
    }}
    #noteModal textarea {{
      width: 100%; min-height: 120px; background: rgba(255,255,255,.02); color: var(--fg);
      border: 1px solid var(--panel-border); border-radius: 12px; padding: 12px; resize: vertical;
    }}

    @media (max-width: 800px) {{
      .hq-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="hq-container">
    <h1 class="hq-title">{html.escape(name)} <span class="pulse" aria-hidden="true"></span></h1>
    <p class="hq-subtitle">{html.escape(motto)}</p>

    <section class="hq-panel">
      <div class="stripe"></div>

      <div class="hq-grid">
        <!-- Портал -->
        <div class="card">
          <h3>Портал</h3>
          <div class="pills">
            <span class="pill pill--intro">Stable</span>
            <span class="pill pill--reflect">Online</span>
            <span class="pill pill--transition">Light active</span>
          </div>
          <hr class="sep" style="opacity:.25;margin:12px 0;">
          <div class="small hq-breadcrumbs">
            <span class="badge"><span class="dot"></span> HQ Panel</span>
            <span class="badge"><span class="dot"></span> Cycle Active</span>
            <span class="badge"><span class="dot"></span> Memory Stable</span>
            <span class="badge"><span class="dot"></span> Reflection On</span>
          </div>
        </div>

        <!-- Рефлексия -->
        <div class="card reflect-box">
          <h3>Reflection · последняя заметка</h3>
          <div class="reflect-text" id="reflection-text">—</div>
          <div class="reflect-footer">
            <span id="last-upd">—</span>
            <button class="btn" id="addNoteBtn">Добавить заметку</button>
          </div>
        </div>
      </div>

      <!-- Core · счётчики -->
      <div class="card" style="margin: 12px 0 6px;">
        <h3>Core · состояние</h3>
        <div class="pills" style="margin-top:10px">
          <span class="pill">users: <b id="users">0</b></span>
          <span class="pill pill--intro">intro: <b id="intro">0</b></span>
          <span class="pill pill--reflect">reflect: <b id="reflect">0</b></span>
          <span class="pill pill--transition">transition: <b id="transition">0</b></span>
        </div>
      </div>

      <div class="hq-status">
        <span class="badge"><span class="dot"></span> HQ Panel</span>
        <span class="badge"><span class="dot"></span> Cycle Active</span>
        <span class="badge"><span class="dot"></span> Memory Stable</span>
        <span class="badge"><span class="dot"></span> Reflection On</span>
      </div>
    </section>
  </div>

  <!-- Модалка добавления заметки -->
  <div id="noteModal">
    <div class="box">
      <h3 style="margin:0 0 10px;">Reflection · новая заметка</h3>
      <form id="noteForm">
        <textarea name="text" placeholder="Введите заметку..."></textarea>
        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:12px;">
          <button class="btn" type="submit">Сохранить</button>
          <button class="btn" type="button" id="closeModal" style="background:linear-gradient(180deg,#e6e6e6,#cfcfcf);color:#111;">Отмена</button>
        </div>
      </form>
    </div>
  </div>

  <script>
    const $ = (s)=>document.querySelector(s);
    const modal=$("#noteModal"), form=$("#noteForm");

    async function pull(){
      try{
        const r = await fetch("/ui/stats.json", {cache:"no-store"});
        if(!r.ok) return;
        const d = await r.json();
        const c = d.core || {intro:0,reflect:0,transition:0,users:0,last_updated:""};
        const refl = d.reflection || {text:null,updated_at:null};

        $("#users").textContent      = c.users ?? 0;
        $("#intro").textContent      = c.intro ?? 0;
        $("#reflect").textContent    = c.reflect ?? 0;
        $("#transition").textContent = c.transition ?? 0;
        $("#last-upd").textContent   = c.last_updated || "—";
        $("#reflection-text").textContent = (refl.text && String(refl.text).trim()) ? refl.text : "—";
      }catch(e){ console.debug("stats fetch failed", e); }
    }

    $("#addNoteBtn").onclick = () => { form.reset(); modal.style.display="flex"; };
    $("#closeModal").onclick = () => { modal.style.display="none"; };

    form.onsubmit = async (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      const res = await fetch("/ui/reflection/save", {{ method: "POST", body: fd }});
      if(res.ok){
        modal.style.display="none";
        pull();
      }else{
        alert("Ошибка сохранения");
      }
    };

    pull();
    setInterval(pull, 8000);
  </script>
</body>
</html>
    """
    return HTMLResponse(html_page)
