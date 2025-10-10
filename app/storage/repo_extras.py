from __future__ import annotations
import logging
from typing import Optional

log = logging.getLogger(__name__)

async def save_casting(
    *,
    tg_id: int,
    name: str,
    age: int,
    city: str,
    experience: str,
    contact: str,
    portfolio: Optional[str],
    agree_contact: bool = True,
) -> None:
    log.info(
        "[extras] save_casting(tg_id=%s): name=%r, age=%s, city=%r, exp=%r, contact=%r, portfolio=%r, agree=%s",
        tg_id, name, age, city, experience, contact, portfolio, agree_contact,
    )
