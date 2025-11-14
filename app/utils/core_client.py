import os
import aiohttp

CORE_BASE_URL = os.getenv("CORE_BASE_URL", "").rstrip("/")
CORE_GUARD_KEY = os.getenv("CORE_GUARD_KEY", "")

async def core_event(source: str, scene: str, payload: dict):
    """
    Отправляет событие в StageCoach CORE через /api/event.
    """
    if not CORE_BASE_URL:
        return

    url = f"{CORE_BASE_URL}/api/event"
    headers = {
        "Content-Type": "application/json",
        "X-Guard-Key": CORE_GUARD_KEY,
    }

    body = {
        "source": source,
        "scene": scene,
        "payload": payload,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, headers=headers) as r:
                await r.text()  # можно логировать
    except Exception as ex:
        # не ломаем бота при ошибке CORE
        print("CORE EVENT ERROR:", ex)
