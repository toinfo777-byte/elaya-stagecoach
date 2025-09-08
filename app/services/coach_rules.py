from __future__ import annotations
import json
from pathlib import Path

# Загружаем drills из файла (поддерживаем и список, и объект с ключом "drills")
try:
    _raw = json.loads(Path("app/texts/drills.json").read_text(encoding="utf-8"))
except Exception:
    _raw = []

_DRILLS: list[dict] = (
    _raw["drills"] if isinstance(_raw, dict) and "drills" in _raw
    else list(_raw) if isinstance(_raw, list)
    else []
)

# Безопасный дефолт, если файл пуст/битый
_FALLBACK = {
    "id": "breath_reset",
    "title": "Сброс дыхания",
    "steps": [
        "3 тихих вдоха носом",
        "мягкий выдох через рот",
        "расслабь плечи",
        "повтори 2 раза",
    ],
    "check_question": "Стало ли легче дышать и говорить?",
}


def _by_id(key: str) -> dict:
    for d in _DRILLS:
        if d.get("id") == key:
            return d
    return _DRILLS[0] if _DRILLS else _FALLBACK


def pick_drill_by_keywords(q: str) -> dict:
    ql = (q or "").lower()
    if any(w in ql for w in ["зажим", "горле", "горло", "голос", "свобод", "тепле"]):
        return _by_id("voice_warmup")
    if any(w in ql for w in ["взгляд", "вертикаль", "шир", "контакт", "глаза"]):
        return _by_id("eye_contact")
    return _by_id("breath_reset")
