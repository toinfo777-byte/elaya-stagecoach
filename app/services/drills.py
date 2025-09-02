import json, random
from pathlib import Path
from sqlalchemy.orm import Session
from app.storage.models import Drill, User

_DRILLS_PATH = Path(__file__).resolve().parents[1] / "texts" / "drills.json"

def load_drills_from_json() -> list[dict]:
    return json.loads(_DRILLS_PATH.read_text(encoding="utf-8"))

def ensure_drills_in_db(session: Session) -> None:
    """Если в БД нет этюдов — загрузить из JSON один раз."""
    if session.query(Drill).count() == 0:
        for d in load_drills_from_json():
            session.add(Drill(id=d["id"], payload_json=d))
        session.commit()

def choose_drill_for_user(session: Session, user: User) -> Drill:
    """Пока просто случайно. (Потом учтём профиль из мини-кастинга.)"""
    drills = session.query(Drill).all()
    return random.choice(drills)
