from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON, Boolean

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    name: Mapped[str | None] = mapped_column(String(255))
    tz: Mapped[str | None] = mapped_column(String(64))
    goal: Mapped[str | None] = mapped_column(String(255))
    exp_level: Mapped[int | None] = mapped_column(Integer)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime)
    consent_at: Mapped[datetime | None] = mapped_column(DateTime)

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(64))
    payload_json: Mapped[dict] = mapped_column(JSON, default={})
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
