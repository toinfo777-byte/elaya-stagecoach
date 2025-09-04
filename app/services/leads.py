from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from datetime import datetime
import csv
import os

from sqlalchemy.orm import Session

from app.storage.models import Lead


@dataclass
class LeadPayload:
    channel: str
    contact: str
    note: str | None = None


def create_lead(s: Session, user_id: int, payload: LeadPayload) -> Lead:
    lead = Lead(
        user_id=user_id,
        channel=payload.channel,
        contact=payload.contact.strip(),
        note=(payload.note or "").strip(),
        ts=datetime.utcnow(),
    )
    s.add(lead)
    s.commit()
    s.refresh(lead)
    return lead


def export_leads_csv(s: Session, file_path: str) -> str:
    """Выгружает все лиды в CSV и возвращает путь к файлу."""
    rows: Iterable[Lead] = s.query(Lead).order_by(Lead.ts.desc()).all()
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id", "user_id", "channel", "contact", "note", "ts"])
        for r in rows:
            w.writerow([r.id, r.user_id, r.channel, r.contact, r.note or "", r.ts.isoformat()])
    return file_path
