from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from threading import Lock
from typing import List, Dict, Any


@dataclass
class CoreState:
    """Мини-память и состояние ядра."""
    cycle: int = 0
    last_update: str = "-"
    intro: int = 0
    reflect: int = 0
    transition: int = 0
    events: List[Dict[str, Any]] = field(default_factory=list)
    reflection: Dict[str, Any] = field(
        default_factory=lambda: {"text": "", "updated_at": "-"}
    )

    def snapshot(self) -> Dict[str, Any]:
        return asdict(self)


class StateStore:
    _instance: "StateStore | None" = None
    _lock = Lock()

    def __init__(self) -> None:
        self.state = CoreState()
        self._state_lock = Lock()

    @classmethod
    def get(cls) -> "StateStore":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = StateStore()
        return cls._instance

    # --- helpers ---

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    # --- бизнес-операции ---

    def sync(
        self,
        source: str = "manual",
        scene: str | None = None,
        payload: Dict[str, Any] | None = None,
    ) -> CoreState:
        """
        Инкремент цикла + запись события.
        """
        with self._state_lock:
            self.state.cycle += 1
            now = self._now_iso()
            self.state.last_update = now

            evt = {
                "ts": now,
                "cycle": self.state.cycle,
                "source": source,
                "scene": scene or "transition",
                "payload": payload or {},
            }
            self._append_event(evt)
            return self.state

    def add_event(
        self,
        source: str,
        scene: str | None = None,
        payload: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Пишет событие в таймлайн без изменения цикла.
        Возвращает записанное событие.
        """
        with self._state_lock:
            now = self._now_iso()
            evt = {
                "ts": now,
                "cycle": self.state.cycle,
                "source": source,
                "scene": scene or "other",
                "payload": payload or {},
            }
            self._append_event(evt)
            return evt

    def _append_event(self, evt: Dict[str, Any]) -> None:
        self.state.events.insert(0, evt)
        # держим последние 50 событий
        self.state.events = self.state.events[:50]

    def get_state(self) -> CoreState:
        with self._state_lock:
            return self.state

    def get_timeline(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._state_lock:
            return self.state.events[:limit]

    def set_reflection(self, text: str) -> Dict[str, Any]:
        """
        Обновляет reflection и добавляет событие в таймлайн.
        """
        with self._state_lock:
            now = self._now_iso()
            self.state.reflection = {"text": text, "updated_at": now}
            self._append_event(
                {
                    "ts": now,
                    "cycle": self.state.cycle,
                    "source": "reflection",
                    "scene": "reflect",
                    "payload": {"note": text},
                }
            )
            return self.state.reflection
