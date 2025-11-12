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

    # бизнес-операции
    def sync(self, source: str = "manual") -> CoreState:
        with self._state_lock:
            self.state.cycle += 1
            self.state.last_update = datetime.now(timezone.utc).isoformat()
            self._push_event("sync", {"source": source, "cycle": self.state.cycle})
            return self.state

    def _push_event(self, kind: str, payload: Dict[str, Any]) -> None:
        evt = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "kind": kind,
            "payload": payload,
        }
        self.state.events.insert(0, evt)
        # держим последние 20
        self.state.events = self.state.events[:20]

    def get_state(self) -> CoreState:
        with self._state_lock:
            return self.state
