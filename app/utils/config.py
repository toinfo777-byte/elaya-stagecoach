# app/utils/config.py
from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    bot_token: str

def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()

settings = Settings(
    bot_token=_env("BOT_TOKEN"),  # в Render переменная окружения BOT_TOKEN
)
