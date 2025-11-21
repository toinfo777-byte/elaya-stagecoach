# app/core/cycle_state.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass
class CycleState:
    """
    Высокоуровневое представление состояния цикла Элайи.

    Это надстройка над "сырым" core-состоянием:
    - cycle        — номер цикла
    - phase        — текущая фаза (intro / reflect / transition / next / idle)
    - started_at   — время первого события (условное начало цикла)
    - updated_at   — последнее обновление ядра
    - last_event_* — информация о последнем событии
    - total_*      — счётчики по фазам
    """

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

    @classmethod
    def from_core(cls, core: Dict[str, Any]) -> "CycleState":
        """
        Собираем CycleState из core.to_dict(), не трогая сам store.
        """
        cycle = int(core.get("cycle", 0) or 0)
        intro_count = int(core.get("intro", 0) or 0)
        reflect_count = int(core.get("reflect", 0) or 0)
        transition_count = int(core.get("transition", 0) or 0)

        last_update = core.get("last_update") or "-"
        events: List[Dict[str, Any]] = core.get("events") or []

        if events:
            last_event = events[-1]
            phase = (last_event.get("scene") or "idle").strip() or "idle"
            last_ts = last_event.get("ts", "-")
            source = last_event.get("source", "") or ""
            started_at = events[0].get("ts", "-")
        else:
            phase = "idle"
            last_ts = "-"
            source = ""
            started_at = "-"

        updated_at = last_update if last_update not in (None, "", "-") else last_ts

        return cls(
            cycle=cycle,
            phase=phase,
            started_at=started_at,
            updated_at=updated_at,
            last_event_ts=last_ts,
            last_event_scene=phase,
            last_event_source=source,
            total_intro=intro_count,
            total_reflect=reflect_count,
            total_transition=transition_count,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
