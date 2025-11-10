# app/routes/diag.py
from __future__ import annotations
from fastapi import APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse
from app.core import store

router = APIRouter(prefix="/diag")

@router.get("/ping")
async def ping():
    return PlainTextResponse("pong")

@router.get("/status_json")
async def status_json():
    st = store.get_stats()
    return JSONResponse({
        "ok": True,
        "users": st["users"],
        "last_updated": st["last_updated"],
        "scenes": st["scene_counts"],
        "last_reflect": st["last_reflect"],
    })
