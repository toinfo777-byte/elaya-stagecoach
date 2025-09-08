import json, re
from pathlib import Path

_DRILLS = json.loads(Path("app/texts/drills.json").read_text(encoding="utf-8"))

def pick_drill_by_keywords(q: str) -> dict:
    ql = q.lower()
    # грубая эвристика — расширишь по мере необходимости
    if any(w in ql for w in ["зажим", "горле", "голос", "свобод", "тепле"]):
        key = "voice_warmup"
    elif any(w in ql for w in ["взгляд", "вертикаль", "шир", "контакт"]):
        key = "eye_contact"
    else:
        key = "breath_reset"
    for d in _DRILLS["drills"]:
        if d["id"] == key:
            return d
    return _DRILLS["drills"][0]
