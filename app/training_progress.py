from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Any
import json


DATA_PATH = Path(__file__).resolve().parent / "data" / "training_progress.json"
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_data() -> Dict[str, List[str]]:
    if not DATA_PATH.exists():
        return {}
    try:
        with DATA_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_data(data: Dict[str, List[str]]) -> None:
    with DATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_training_day(user_id: int, d: date | None = None) -> None:
    if d is None:
        d = date.today()

    data = _load_data()
    key = str(user_id)
    days = set(data.get(key, []))
    days.add(d.isoformat())
    data[key] = sorted(days)
    _save_data(data)


def get_progress_summary(user_id: int, limit: int = 7) -> dict:
    data = _load_data()
    key = str(user_id)
    day_strings = data.get(key, [])

    if not day_strings:
        return {"total_days": 0, "current_streak": 0, "last_date": None}

    days = [date.fromisoformat(s) for s in day_strings]
    days.sort()

    total_days = len(days)
    last_date = days[-1]

    streak = 1
    cur = last_date
    idx = len(days) - 2
    while idx >= 0:
        prev = days[idx]
        if (cur - prev) <= timedelta(days=1):
            streak += 1
            cur = prev
            idx -= 1
        else:
            break

    return {
        "total_days": total_days,
        "current_streak": streak,
        "last_date": last_date.isoformat(),
    }
