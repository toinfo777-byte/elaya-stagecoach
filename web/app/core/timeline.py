# web/app/core/timeline.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List

# Простой in-memory таймлайн для локальной разработки.
# Если захочешь — потом легко заменим на SQLite/Redis.

@dataclass(frozen=True)
class TimelineRow:
    ts: str
    source: str
    scene: str
    payload: Dict[str, Any]


_EVENTS: List[TimelineRow] = []


def add_event(source: str, scene: str, payload: Dict[str, Any]) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    _EVENTS.append(TimelineRow(ts=ts, source=source, scene=scene, payload=payload))


def get_timeline(limit: int = 50) -> List[Dict[str, Any]]:
    limit = max(1, min(int(limit), 500))
    return [asdict(x) for x in _EVENTS[-limit:]][::-1]
