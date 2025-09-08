from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import csv, os
from sqlalchemy.orm import Session
from app.storage.models import Feedback

@dataclass
class FeedbackPayload:
    context: str
    context_id: str | None = None
    score: int | None = None
    text: str | None = None
    voice_file_id: str | None = None
    first_source: str | None = None

def create_feedback(s: Session, user_id: int, p: FeedbackPayload) -> Feedback:
    fb = Feedback(
        user_id=user_id,
        first_source=p.first_source,
        context=p.context,
        context_id=p.context_id,
        score=p.score,
        text=p.text,
        voice_file_id=p.voice_file_id,
        created_at=datetime.utcnow(),
    )
    s.add(fb)
    s.commit()
    s.refresh(fb)
    return fb

def export_feedback_csv(s: Session, file_path: str, since: datetime | None = None) -> str:
    q = s.query(Feedback).order_by(Feedback.created_at.desc())
    if since:
        q = q.filter(Feedback.created_at >= since)
    rows = q.all()
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id","user_id","first_source","context","context_id","score","text","voice_file_id","created_at"])
        for r in rows:
            w.writerow([
                r.id, r.user_id, r.first_source or "", r.context, r.context_id or "",
                r.score if r.score is not None else "", r.text or "", r.voice_file_id or "", r.created_at.isoformat()
            ])
    return file_path
