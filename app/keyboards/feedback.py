from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Нормализованный формат callback_data, который понимает feedback router:
#   fb:emoji:<fire|ok|meh>|cat:<training|casting|other>|id:<123>
#   fb:phrase|cat:<...>|id:<...>

def _cb(parts: list[str]) -> str:
    return "|".join(parts)

def feedback_kb(category: str, entity_id: str) -> InlineKeyboardMarkup:
    cat = f"cat:{category}"
    rid = f"id:{entity_id}"
    row1 = [
        InlineKeyboardButton(text="🔥", callback_data=_cb(["fb:emoji:fire", cat, rid])),
        InlineKeyboardButton(text="👌", callback_data=_cb(["fb:emoji:ok", cat, rid])),
        InlineKeyboardButton(text="😐", callback_data=_cb(["fb:emoji:meh", cat, rid])),
    ]
    row2 = [
        InlineKeyboardButton(text="✍️ 1 фраза", callback_data=_cb(["fb:phrase", cat, rid]))
    ]
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2])
