from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

from app.core import store

SceneName = Literal["intro", "reflect", "transition"]


@dataclass
class SceneState:
    last: SceneName = "intro"
    last_reflect: str | None = None


class SceneEngine:
    def __init__(self) -> None:
        # БД инициализируется в app/main.py (@app.on_event("startup"))
        pass

    def _load(self, user_id: int) -> SceneState:
        row = store.get_scene(user_id)
        if not row:
            return SceneState()
        return SceneState(last=row.last_scene, last_reflect=row.last_reflect)

    def intro(self, user_id: int) -> str:
        st = self._load(user_id)
        st.last = "intro"
        store.upsert_scene(user_id, last_scene="intro", last_reflect=st.last_reflect)
        return "🌅 Вход. Вдох — настрой внимание. Скажи одно слово о своём состоянии."

    def reflect(self, user_id: int, text: str | None) -> str:
        st = self._load(user_id)
        st.last = "reflect"

        t = (text or "").strip()
        if t:
            # фиксируем сцену и последнюю рефлексию
            store.upsert_scene(user_id, last_scene="reflect", last_reflect=t)
            reply = f"🌕 Слышу: «{t}». Что в этом было светлым?"
        else:
            # пустой ввод — сцену переключаем, рефлексию не трогаем
            store.upsert_scene(user_id, last_scene="reflect", last_reflect=st.last_reflect)
            reply = "🌕 Отрази день одной фразой. Что было самым светлым?"

        return reply

    def transition(self, user_id: int) -> str:
        st = self._load(user_id)
        st.last = "transition"
        store.upsert_scene(user_id, last_scene="transition", last_reflect=st.last_reflect)
        return "🌄 Переход. Выбери одно маленькое действие до завтра — и сделай его."


engine = SceneEngine()
