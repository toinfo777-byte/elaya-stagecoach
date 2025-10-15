from __future__ import annotations
import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str = Field(..., alias="BOT_TOKEN")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    sentry_dsn: Optional[str] = Field(None, alias="SENTRY_DSN")
    healthchecks_url: Optional[str] = Field(None, alias="HEALTHCHECKS_URL")
    healthchecks_interval: int = Field(300, alias="HEALTHCHECKS_INTERVAL")
    healthchecks_startup_grace: int = Field(10, alias="HEALTHCHECKS_STARTUP_GRACE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
