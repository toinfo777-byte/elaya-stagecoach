# app/config.py
from __future__ import annotations
import os


class Settings:
    BOT_TOKEN: str
    DB_URL: str

    def __init__(self) -> None:
        self.BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
        # по умолчанию локальный файл в /data (Render), либо /tmp
        self.DB_URL = os.environ.get("DATABASE_URL", "sqlite:////data/db.sqlite").strip()


settings = Settings()
