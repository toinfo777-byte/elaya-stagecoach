# app/storage/repo_extras.py
from datetime import datetime
from sqlalchemy import insert, update
from app.storage.db import async_session
from app.storage.models_extras import CastingSession, Feedback, LeaderPath, PremiumRequest

async def save_casting_session(user_id: int, answers: list, result: str):
    async with async_session() as s:
        await s.execute(insert(CastingSession).values(
            user_id=user_id,
            answers=answers,
            result=result,
            finished_at=datetime.utcnow(),
            source="mini",
        ))
        await s.commit()

# emoji делаем Optional[str], чтобы можно было сохранять «только текст»
async def save_feedback(user_id: int, emoji: str | None, phrase: str | None):
    async with async_session() as s:
        await s.execute(insert(Feedback).values(
            user_id=user_id,
            emoji=emoji or "",
            phrase=phrase,
        ))
        await s.commit()

async def save_leader_intent(user_id: int, intent: str, micro_note: str | None, upsert: bool = False):
    async with async_session() as s:
        if upsert:
            await s.execute(
                update(LeaderPath)
                .where(LeaderPath.user_id == user_id)
                .values(intent=intent, micro_note=micro_note)
            )
        else:
            await s.execute(insert(LeaderPath).values(
                user_id=user_id, intent=intent, micro_note=micro_note, source="leader"
            ))
        await s.commit()

async def save_premium_request(user_id: int, text: str, source: str):
    async with async_session() as s:
        await s.execute(insert(PremiumRequest).values(
            user_id=user_id, text=text, source=source
        ))
        await s.commit()
