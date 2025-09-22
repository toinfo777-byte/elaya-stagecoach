from __future__ import annotations

from datetime import date, timedelta
from sqlalchemy import select, func, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.storage.models import (
    Base,
    engine,
    async_session_maker,
    Profile,
    TrainingLog,
    CastingForm,
)

# ---------- INIT ----------
async def ensure_schema() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ---------- Repo-класс ----------
class Repo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def delete_user(self, tg_id: int) -> None:
        """Удалить пользователя и все его записи."""
        await self.session.execute(delete(Profile).where(Profile.tg_id == tg_id))
        await self.session.execute(delete(TrainingLog).where(TrainingLog.tg_id == tg_id))
        await self.session.execute(delete(CastingForm).where(CastingForm.tg_id == tg_id))
        await self.session.commit()


# ---------- Profile ----------
async def upsert_profile(tg_id: int, username: str | None, name: str | None) -> None:
    async with async_session_maker() as session:
        q = await session.execute(select(Profile).where(Profile.tg_id == tg_id))
        p = q.scalar_one_or_none()
        if p is None:
            p = Profile(tg_id=tg_id, username=username, name=name)
            session.add(p)
        else:
            p.username = username or p.username
            p.name = name or p.name
        await session.commit()


# ---------- Training ----------
async def log_training(tg_id: int, level: str, done: bool) -> None:
    async with async_session_maker() as session:
        session.add(
            TrainingLog(
                tg_id=tg_id,
                date=date.today(),
                level=level,
                done=done,
            )
        )
        await session.commit()


async def calc_progress(tg_id: int) -> tuple[int, int]:
    from datetime import date, timedelta
    async with async_session_maker() as session:
        # last7
        since = date.today() - timedelta(days=6)
        r7 = await session.execute(
            select(func.count())
            .select_from(TrainingLog)
            .where(
                TrainingLog.tg_id == tg_id,
                TrainingLog.done.is_(True),
                TrainingLog.date >= since,
            )
        )
        last7 = int(r7.scalar() or 0)

        # streak
        r = await session.execute(
            select(TrainingLog.date)
            .where(TrainingLog.tg_id == tg_id, TrainingLog.done.is_(True))
            .order_by(desc(TrainingLog.date))
        )
        days = [row[0] for row in r.all()]
        cur = date.today()
        streak = 0
        sset = set(days)
        while cur in sset:
            streak += 1
            cur = cur - timedelta(days=1)

        return streak, last7


# ---------- Casting ----------
async def save_casting(
    tg_id: int,
    name: str,
    age: int,
    city: str,
    experience: str,
    contact: str,
    portfolio: str | None,
    agree_contact: bool,
) -> None:
    async with async_session_maker() as session:
        session.add(
            CastingForm(
                tg_id=tg_id,
                name=name,
                age=age,
                city=city,
                experience=experience,
                contact=contact,
                portfolio=portfolio,
                agree_contact=agree_contact,
            )
        )
        await session.commit()
