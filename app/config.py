# app/config.py
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    bot_token: str = Field(..., env="BOT_TOKEN")
    bot_profile: str = Field("trainer", env="BOT_PROFILE")  # 'hq' | 'trainer'
    admin_alert_chat_id: int | None = Field(default=None, env="ADMIN_ALERT_CHAT_ID")

    # алерты
    alert_source: str = Field("web", env="ALERT_SOURCE")  # 'web'|'bot'
    alert_dedup_window_sec: int = Field(15, env="ALERT_DEDUP_WINDOW_SEC")

    @property
    def is_hq(self) -> bool:
        return self.bot_profile.lower() == "hq"

settings = Settings()
