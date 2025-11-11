# app/core_api.py
from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from os import getenv

from app.core.scene_engine import engine
from app.core import store

router = APIRouter(prefix="/api")


class SceneRequest(BaseModel):
    user_id: int
    chat_id: int
    text: str | None = None
    scene: str


class SceneResponse(BaseModel):
    reply: str


def _auth(x_core_token: str | None):
    if not x_core_token or x_core_token != getenv("CORE_API_TOKEN"):
        raise HTTPException(status_code=401, detail="unauthorized")


@router.post("/scene/enter", response_model=SceneResponse)
async def scene_enter(req: SceneRequest, x_core_token: str | None = Header(None)):
    _auth(x_core_token)
    return SceneResponse(reply=engine.intro(req.user_id))


@router.post("/scene/reflect", response_model=SceneResponse)
async def scene_reflect(req: SceneRequest, x_core_token: str | None = Header(None)):
    _auth(x_core_token)
    reply = engine.reflect(req.user_id, req.text)
    if req.text and str(req.text).strip():
        # фиксируем отражение в журнале
        store.add_reflection(req.user_id, str(req.text))
    return SceneResponse(reply=reply)


@router.post("/scene/transition", response_model=SceneResponse)
async def scene_transition(req: SceneRequest, x_core_token: str | None = Header(None)):
    _auth(x_core_token)
    return SceneResponse(reply=engine.transition(req.user_id))
