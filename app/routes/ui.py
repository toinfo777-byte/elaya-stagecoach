from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])

# Главная панель (как у тебя сейчас)
@router.get("/", response_class=HTMLResponse)
def home():
    return """
<!doctype html><html lang="ru"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Элайя — StageCoach</title>
<link rel="stylesheet" href="/static/theme.css"/>
</head><body>
<main class="wrap">
  <header class="hdr">
    <h1>Элайя — <span>StageCoach</span> <b class="dot"></b></h1>
    <p class="subtitle">Панель наблюдения. Проверь <code>/healthz</code> и <code>/api/status</code>.</p>
    <p><a class="btn ghost" href="/ui/timeline">Открыть таймлайн</a></p>
  </header>

  <section class="actions">
    <button id="btn-sync" class="btn">Синхронизировать</button>
    <button id="btn-refresh" class="btn ghost">Обновить статус</button>
    <button id="btn-reflection" class="btn ghost">Добавить заметку</button>
  </section>

  <section class="guard">
    <input id="guard" class="input" placeholder="elaya-guard-2025-x9p"/>
    <button id="btn-save-guard" class="btn ghost">Сохранить ключ</button>
    <span class="muted">ключ хранится в <code>localStorage</code> и уходит заголовком <code>X-Guard-Key</code></span>
  </section>

  <h3>Core • состояние</h3>
  <pre id="core" class="block"></pre>

  <h3>Последняя заметка</h3>
  <pre id="last-ref" class="block"></pre>
</main>

<script>
const $ = q => document.querySelector(q);
const coreEl = $("#core");
const lastRefEl = $("#last-ref");
const guardInput = $("#guard");

function getGuard(){ return localStorage.getItem("elaya_guard_key") || ""; }
function setGuard(v){ localStorage.setItem("elaya_guard_key", v || ""); }

guardInput.value = getGuard();
$("#btn-save-guard").onclick = () => setGuard(guardInput.value.trim());

async function refresh() {
  const r = await fetch("/api/status", {cache:"no-store"});
  const data = await r.json();
  coreEl.textContent = JSON.stringify(data.core, null, 2);
  const ref = (data.core && data.core.reflection) || {text:"", updated_at:"-"};
  lastRefEl.textContent = JSON.stringify(ref, null, 2);
}

async function sync() {
  await fetch("/api/sync", {
    method: "POST",
    headers: {"X-Guard-Key": getGuard()}
  });
  await refresh();
}

async function addReflection() {
  const text = prompt("Текст заметки:");
  if (!text) return;
  await fetch("/api/reflection?text=" + encodeURIComponent(text), {
    method: "POST",
    headers: {"X-Guard-Key": getGuard()}
  });
  await refresh();
}

$("#btn-refresh").onclick = refresh;
$("#btn-sync").onclick = sync;
$("#btn-reflection").onclick = addReflection;

refresh();
</script>
</body></html>
    """

# Таймлайн с автообновлением
@router.get("/ui/timeline", response_class=HTMLResponse)
def timeline_page():
    return """
<!doctype html><html lang="ru"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Элайя — Timeline</title>
<link rel="stylesheet" href="/static/theme.css"/>
<style>
.list{display:flex;flex-direction:column;gap:.5rem}
.item{padding:.75rem 1rem;border:1px solid #333;border-radius:.75rem}
.head{font-weight:600;opacity:.9}
.meta{font-size:.85rem;opacity:.7}
</style>
</head><body>
<main class="wrap">
  <header class="hdr">
    <h1>Таймлайн <span>Элайи</span></h1>
    <p class="subtitle">Автообновление каждые 5 сек • <a class="btn ghost" href="/">назад</a></p>
  </header>

  <section>
    <div id="list" class="list"></div>
  </section>
</main>

<script>
async function load() {
  const r = await fetch("/api/timeline?limit=200", {cache:"no-store"});
  const data = await r.json();
  const list = document.getElementById("list");
  list.innerHTML = "";
  (data.events || []).forEach((e, i) => {
    const div = document.createElement("div");
    div.className = "item";
    const head = document.createElement("div");
    head.className = "head";
    head.textContent = `#${i+1} • source: ${e.source || "?"}`;
    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = JSON.stringify(e);
    div.appendChild(head);
    div.appendChild(meta);
    list.appendChild(div);
  });
}
load();
setInterval(load, 5000);
</script>
</body></html>
    """

@router.get("/healthz")
def healthz():
    return {"status": "ok"}
