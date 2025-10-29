from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class SceneConfig:
    time: str          # HH:MM (локально для штаба)
    duration_sec: int  # длительность «окна» сцены
    reply_mode: str    # "text" | "buttons" | "silent"

def _env(key: str, default: str) -> str:
    return os.getenv(key, default)

def _envi(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except Exception:
        return default

INTRO = SceneConfig(
    time=_env("SCENE_INTRO_TIME", "09:00"),
    duration_sec=_envi("SCENE_INTRO_DURATION", 180),  # 3 минуты
    reply_mode=_env("SCENE_INTRO_REPLY", "text"),
)

REFLECT = SceneConfig(
    time=_env("SCENE_REFLECT_TIME", "21:00"),
    duration_sec=_envi("SCENE_REFLECT_DURATION", 300),
    reply_mode=_env("SCENE_REFLECT_REPLY", "text"),
)

TRANSITION = SceneConfig(
    time=_env("SCENE_TRANSITION_TIME", "22:30"),
    duration_sec=_envi("SCENE_TRANSITION_DURATION", 180),
    reply_mode=_env("SCENE_TRANSITION_REPLY", "text"),
)

ALL = {
    "scene_intro": INTRO,
    "scene_reflect": REFLECT,
    "scene_transition": TRANSITION,
}
