from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])

# ... твои уже существующие роуты ...

@router.get("/timeline", response_class=HTMLResponse)
def timeline_page():
    return """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Таймлайн Элайи</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>
    body{font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 24px; color:#e7e7e7; background:#0b0d10}
    h1{font-size:22px; margin:0 0 16px}
    .wrap{max-width:880px}
    .row{display:flex;gap:8px; margin:8px 0 16px}
    input,button,textarea{background:#13161a;color:#e7e7e7;border:1px solid #2a2f36;border-radius:8px;padding:10px 12px}
    input,textarea{flex:1}
    button{cursor:pointer}
    .card{border:1px solid #20252c;border-radius:12px;padding:14px;margin:10px 0;background:#0f1216}
    .meta{opacity:.7;font-size:12px}
    .src{opacity:.8}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Таймлайн Элайи</h1>

    <div class="row">
      <input id="text" placeholder="Текст события…">
      <input id="source" value="ui" style="max-width:200px">
      <button id="add">Добавить</button>
    </div>

    <div class="row">
      <input id="guard" placeholder="X-Guard-Key (опционально)">
      <button id="save-guard">Сохранить ключ</button>
      <button id="reload">Обновить</button>
    </div>

    <div id="list"></div>
  </div>

<script>
const $ = (q) => document.querySelector(q);
const list = $("#list");
const guardInput = $("#guard");

// init guard from localStorage
guardInput.value = localStorage.getItem("guardKey") || "";

$("#save-guard").onclick = () => {
  localStorage.setItem("guardKey", guardInput.value.trim());
  alert("Guard key сохранён.");
};

async function load() {
  const r = await fetch("/api/timeline?limit=200", {cache:"no-store"});
  const data = await r.json();
  render(data.events || []);
}
$("#reload").onclick = load;

function render(events) {
  list.innerHTML = "";
  if (!events.length) {
    list.innerHTML = '<p class="meta">Пока нет событий.</p>';
    return;
  }
  for (const e of events) {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <div>${e.text || ""}</div>
      <div class="meta"><span class="src">source: ${e.source}</span> • ${e.created_at}</div>
    `;
    list.appendChild(card);
  }
}

$("#add").onclick = async () => {
  const text = $("#text").value.trim();
  const source = $("#source").value.trim() || "ui";
  if (!text) return;
  const headers = {};
  const key = (guardInput.value || "").trim();
  if (key) headers["X-Guard-Key"] = key;

  const params = new URLSearchParams({text, source});
  const r = await fetch("/api/timeline?" + params.toString(), {
    method: "POST",
    headers
  });
  if (r.ok) {
    $("#text").value = "";
    load();
  } else {
    const err = await r.json().catch(()=>({detail:"error"}));
    alert("Ошибка: " + (err.detail || r.status));
  }
};

// auto-refresh
load();
setInterval(load, 5000);
</script>
</body>
</html>
    """
