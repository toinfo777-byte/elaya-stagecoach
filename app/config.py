import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    admin_ids: tuple[int, ...] = tuple(
        int(x.strip())
        for x in os.getenv("ADMIN_IDS", "").split(",")
        if x.strip()
    )
    db_url: str = os.getenv("DB_URL", "sqlite:///elaya.db")
    env: str = os.getenv("ENV", "dev")

settings = Settings()
