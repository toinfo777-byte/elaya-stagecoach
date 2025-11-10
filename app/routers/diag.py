from __future__ import annotations
from fastapi import APIRouter, Request
from starlette.responses import JSONResponse, PlainTextResponse
from app.core import store

router = APIRouter(prefix="/diag", tags=["diag"])

@router.get("/ping")
async def ping():
    return PlainTextResponse("pong")

@router.post("/webhook")
async def webhook_echo(req: Request):
    # вспомогательный эхо-эндпоинт для проверки входящих тел
    data = await req.json()
    return JSONResponse({"ok": True, "echo": data})

@router.get("/status_json")
async def status_json():
    return JSONResponse(store.get_status_snapshot())

@router.post("/reflection")
async def reflection(req: Request):
    """
    Принять отражение (reflection event) вручную или из внутренних вызовов.
    Тело: {"user_id": 123, "text": "..."} | {"text": "..."}
    """
    data = await req.json()
    text = (data or {}).get("text")
    user_id = (data or {}).get("user_id")
    if not text or not str(text).strip():
        return JSONResponse({"ok": False, "error": "empty text"}, status_code=400)
    store.add_reflection(user_id, str(text))
    return JSONResponse({"ok": True})
