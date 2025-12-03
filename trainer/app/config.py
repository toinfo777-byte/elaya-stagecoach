from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Сказать Pydantic: лишние env-переменные игнорируем, не падаем
    model_config = SettingsConfigDict(extra="ignore")

    # Telegram
    tg_bot_token: str = Field(..., env="TG_BOT_TOKEN")

    # Связь с ядром (Stagecoach Web)
    trainer_core_url: str = Field("", env="TRAINER_CORE_URL")
    trainer_guard_key: str = Field("", env="TRAINER_GUARD_KEY")

    # Прочее
    env: str = Field("dev", env="ENV")
    mode: str = Field("dev", env="MODE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
