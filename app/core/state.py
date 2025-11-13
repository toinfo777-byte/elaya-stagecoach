from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from threading import Lock
from typing import List, Dict, Any


@dataclass
class CoreState:
    """Мини-память и состояние ядра портала."""
    cycle: int = 0
    last_update: str = "-"
    # счётчики фаз портала
    intro: int = 0
    reflect: int = 0
    transition: int = 0
    # лента событий (последние N)
    events: List[Dict[str, Any]] = field(default_factory=list)

    def snapshot(self) -> Dict[str, Any]:
        return asdict(self)


class StateStore:
    _instance: "StateStore | None" = None
    _lock = Lock()

    def __init__(self) -> None:
        self.state = CoreState()
        self._state_lock = Lock()

    # --- singleton ---

    @classmethod
    def get(cls) -> "StateStore":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = StateStore()
        return cls._instance

    # --- внутреннее ---

    def _bump_scene_counter(self, scene: str) -> None:
        """Увеличиваем счётчики фаз портала, если сцена одна из базовых."""
        if scene == "intro":
            self.state.intro += 1
        elif scene == "reflect":
            self.state.reflect += 1
        elif scene == "transition":
            self.state.transition += 1

    def _push_event(self, source: str, scene: str, payload: Dict[str, Any]) -> None:
        """Добавляем событие в ленту (последние N, новые сверху)."""
        evt = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "cycle": self.state.cycle,
            "source": source,
            "scene": scene,
            "payload": payload or {},
        }
        # новые события в начало
        self.state.events.insert(0, evt)
        # держим последние 200
        self.state.events = self.state.events[:200]

    # --- публичные операции ядра ---

    def sync(self, source: str = "ui") -> CoreState:
        """
        Базовая синхронизация ядра.
        Сейчас считаем её сценой 'transition' от заданного source.
        """
        with self._state_lock:
            self.state.cycle += 1
            self.state.last_update = datetime.now(timezone.utc).isoformat()
            scene = "transition"
            self._bump_scene_counter(scene)
            self._push_event(source=source, scene=scene, payload={})
            return self.state

    def add_event(self, source: str, scene: str, payload: Dict[str, Any] | None = None) -> CoreState:
        """
        Добавление произвольного события портала.
        Используется тренером/ботом через /api/event.
        """
        with self._state_lock:
            self.state.cycle += 1
            self.state.last_update = datetime.now(timezone.utc).isoformat()
            self._bump_scene_counter(scene)
            self._push_event(source=source, scene=scene, payload=payload or {})
            return self.state

    def get_state(self) -> CoreState:
        with self._state_lock:
            return self.state
