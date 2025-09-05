from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON, Boolean


class Base(DeclarativeBase):
    ...


# --- Пользователь ---
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

    # ⬇️ НОВОЕ: deep-link источник (/start?start=...)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # связи
    drill_runs: Mapped[list["DrillRun"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    leads: Mapped[list["Lead"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    events: Mapped[list["Event"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    test_results: Mapped[list["TestResult"]] = relationship(back_populates="user", cascade="all, delete-orphan")


# --- Этюд и прохождения ---
class Drill(Base):
    __tablename__ = "drills"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)


class DrillRun(Base):
    __tablename__ = "drill_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    drill_id: Mapped[str] = mapped_column(ForeignKey("drills.id", ondelete="CASCADE"))
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    result_json: Mapped[dict] = mapped_column(JSON, default=dict)
    success_bool: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="drill_runs")
    drill: Mapped["Drill"] = relationship()


# --- Мини-кастинг (на будущее) ---
class Test(Base):
    __tablename__ = "tests"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)


class TestResult(Base):
    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    axes_json: Mapped[dict] = mapped_column(JSON, default=dict)
    score_total: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship(back_populates="test_results")


# --- События ---
class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(64))
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="events")


# --- Лиды ---
class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    channel: Mapped[str] = mapped_column(String(32))          # источник: tg/insta/site/...
    contact: Mapped[str] = mapped_column(String(255))         # @username, телефон, e-mail
    note: Mapped[str | None] = mapped_column(String(500), default=None)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="leads")
