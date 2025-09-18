# app/utils/textmatch.py
from __future__ import annotations

def contains_ci(needle: str):
    """Case-insensitive 'contains' для aiogram F.text.func(...)"""
    n = needle.casefold()
    def _inner(text: str | None) -> bool:
        return isinstance(text, str) and n in text.casefold()
    return _inner
