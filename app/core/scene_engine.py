# app/core/scene_engine.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Dict

SceneName = Literal["intro", "reflect", "transition"]

@dataclass
class SceneState:
    last: SceneName = "intro"

class SceneEngine:
    def __init__(self) -> None:
        self._state: Dict[int, SceneState] = {}

    def _get(self, user_id: int) -> SceneState:
        return self._state.setdefault(user_id, SceneState())

    def intro(self, user_id: int) -> str:
        st = self._get(user_id); st.last = "intro"
        return "🌅 Вход. Вдох — настрой внимание. Скажи одно слово о своём состоянии."

    def reflect(self, user_id: int, text: str | None) -> str:
        st = self._get(user_id); st.last = "reflect"
        if text and text.strip():
            return f"🌕 Слышу: «{text.strip()}». Что в этом было светлым?"
        return "🌕 Отрази день одной фразой. Что было самым светлым?"

    def transition(self, user_id: int) -> str:
        st = self._get(user_id); st.last = "transition"
        return "🌄 Переход. Выбери одно маленькое действие до завтра — и сделай его."

engine = SceneEngine()
