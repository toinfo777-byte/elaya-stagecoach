# app/ui.py
from __future__ import annotations
from fastapi import APIRouter, Response
from app.core import store

router = APIRouter()

@router.get("/ui/stats.json")
async def ui_stats():
    return store.get_stats()

# helper: плейн-текст для ping в браузере
@router.get("/ui/ping")
async def ui_ping():
    return Response(content="ui: ok", media_type="text/plain")
