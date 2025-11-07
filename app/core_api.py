# app/core_api.py
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from os import getenv

router = APIRouter(prefix="/api")


class SceneRequest(BaseModel):
    user_id: int
    chat_id: int
    text: str | None = None
    scene: str  # intro | reflect | transition


class SceneResponse(BaseModel):
    reply: str


def _check_token(token: str | None, header: str | None):
    if not token or not header or header != token:
        raise HTTPException(status_code=401, detail="unauthorized")


@router.post("/scene/enter", response_model=SceneResponse)
async def scene_enter(req: SceneRequest, x_core_token: str | None = Header(None)):
    _check_token(getenv("CORE_API_TOKEN"), x_core_token)
    return SceneResponse(reply="🌅 Вход: дыхание настраивается. Скажи одно слово о своём состоянии.")


@router.post("/scene/reflect", response_model=SceneResponse)
async def scene_reflect(req: SceneRequest, x_core_token: str | None = Header(None)):
    _check_token(getenv("CORE_API_TOKEN"), x_core_token)
    return SceneResponse(reply="🌕 Отрази: что было самым светлым моментом сегодня?")


@router.post("/scene/transition", response_model=SceneResponse)
async def scene_transition(req: SceneRequest, x_core_token: str | None = Header(None)):
    _check_token(getenv("CORE_API_TOKEN"), x_core_token)
    return SceneResponse(reply="🌄 Переход: выбери одно маленькое действие — и сделай его до завтра.")
