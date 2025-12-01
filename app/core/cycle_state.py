# app/core/cycle_state.py
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List
from datetime import datetime, timezone


@dataclass
class CycleState:
    """
    Высокоуровневое состояние цикла Элайи.
    """

    # --- основные поля цикла ---
    cycle: int = 0
    phase: str = "idle"

    started_at: str = "-"
    updated_at: str = "-"

    last_event_ts: str = "-"
    last_event_scene: str = "-"
    last_event_source: str = ""

    total_intro: int = 0
    total_reflect: int = 0
    total_transition: int = 0

    # список сырых событий
    events: List[Dict[str, Any]] = field(default_factory=list)

    # singleton
    _instance: "CycleState" | None = None

    # -------------------------------------------------
    # Singleton доступ
    # -------------------------------------------------
    @classmethod
    def get(cls) -> "CycleState":
        if cls._instance is None:
            cls._instance = CycleState()
        return cls._instance

    # -------------------------------------------------
    # Добавление события
    # -------------------------------------------------
    def append_event(self, source: str, scene: str, payload: Dict[str, Any]) -> None:
        """
        Добавляет событие и обновляет агрегированные поля.
        """
        now_ts = datetime.now(tz=timezone.utc).isoformat()

        event = {
            "ts": now_ts,
            "source": source,
            "scene": scene,
            "payload": payload,
        }
        self.events.append(event)

        # обновление основных полей
        self.last_event_ts = now_ts
        self.last_event_scene = scene
        self.last_event_source = source
        self.updated_at = now_ts

        if self.started_at == "-":
            self.started_at = now_ts  # первое событие цикла

        # обновление фазы
        self.phase = scene

        # обновление счетчиков
        if scene == "intro":
            self.total_intro += 1
        elif scene == "reflect":
            self.total_reflect += 1
        elif scene == "transition":
            self.total_transition += 1

    # -------------------------------------------------
    # Для отладки / API
    # -------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
