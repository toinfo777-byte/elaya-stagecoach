from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])

@router.get("/timeline", response_class=HTMLResponse)
async def timeline():
    return """
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8"/>
    <title>Таймлайн Элайи</title>
    <style>
        body { font-family: sans-serif; background:#050816; color:#fff; padding:20px; }
        h1 { margin-bottom:10px; }
        .event { padding:8px 0; border-bottom:1px solid #333; }
        .ts { color:#7df9ff; }
        .scene { color:#ffa; }
        .payload { color:#adf; }
    </style>
</head>
<body>

<h1>Таймлайн Элайи</h1>
<div id="events">Загрузка…</div>

<script>
async function loadTimeline() {
    const r = await fetch("/api/timeline");
    const data = await r.json();
    const root = document.getElementById("events");

    if (!data.ok) {
        root.innerHTML = "<b>Ошибка загрузки</b>";
        return;
    }

    if (!data.events.length) {
        root.innerHTML = "<i>Пока нет событий</i>";
        return;
    }

    root.innerHTML = data.events
      .map(ev => `
        <div class="event">
            <div class="ts">${ev.ts}</div>
            <div><b>${ev.source}</b> — <span class="scene">${ev.scene}</span></div>
            <div class="payload">${JSON.stringify(ev.payload)}</div>
        </div>
      `)
      .join("");
}

setInterval(loadTimeline, 5000);
loadTimeline();
</script>

</body>
</html>
"""
