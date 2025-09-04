# app/storage/repo.py
from __future__ import annotations
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings
from app.storage.models import Base, User, DrillRun, TestResult, Lead, Event

# --- инициализация БД ---
engine = create_engine(settings.db_url, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

@contextmanager
def session_scope():
    s: Session = SessionLocal()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()

# --- каскадное удаление пользователя и его записей ---
def delete_user_cascade(s: Session, user_id: int) -> None:
    s.query(DrillRun).filter_by(user_id=user_id).delete()
    s.query(TestResult).filter_by(user_id=user_id).delete()
    s.query(Lead).filter_by(user_id=user_id).delete()
    s.query(Event).filter_by(user_id=user_id).delete()
    s.query(User).filter(User.id == user_id).delete()
    s.commit()
