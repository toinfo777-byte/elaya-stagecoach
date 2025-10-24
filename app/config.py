# app/config.py
from __future__ import annotations

import json
from typing import List, Optional

from pydantic import Field, computed_field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
    )

    # базовые
    # В web-режиме токен не обязателен, в worker/bot — обязателен (см. валидатор ниже).
    bot_token: Optional[str] = Field(None, alias="BOT_TOKEN")
    db_url: str = Field("sqlite:////data/db.sqlite", alias="DB_URL")
    env: str = Field("prod", alias="ENV")

    # режимы запуска
    # Поддерживаем синонимы: "worker" и "bot" считаем одним и тем же режимом.
    mode: str = Field("worker", alias="MODE")  # worker|bot | web
    build_sha: Optional[str] = Field(None, alias="BUILD_SHA")
    bot_id: Optional[str] = Field(None, alias="BOT_ID")

    # админы/уведомления
    admin_alert_chat_id: Optional[int] = Field(None, alias="ADMIN_ALERT_CHAT_ID")
    admin_ids_raw: Optional[str] = Field("", alias="ADMIN_IDS")  # строка из ENV

    # опциональные
    channel_username: Optional[str] = Field(None, alias="CHANNEL_USERNAME")
    coach_rate_sec: int = Field(2, alias="COACH_RATE_SEC")
    coach_ttl_min: int = Field(30, alias="COACH_TTL_MIN")

    # ---------- нормализация и валидация ----------

    @field_validator("mode")
    @classmethod
    def normalize_mode(cls, v: str) -> str:
        """Нормализуем режим: приводим к нижнему регистру и маппим 'bot' -> 'worker'."""
        val = (v or "").strip().lower()
        if val == "bot":
            return "worker"
        if val in {"worker", "web"}:
            return val
        # если что-то иное — по умолчанию считаем worker
        return "worker"

    @model_validator(mode="after")
    def check_bot_token_required(self) -> "Settings":
        """В worker/bot режиме BOT_TOKEN обязателен, в web — нет."""
        if self.is_worker:
            if not self.bot_token or self.bot_token.strip().lower() == "dummy":
                raise ValueError("BOT_TOKEN is required in worker/bot mode")
        return self

    # ---------- удобные свойства ----------

    @computed_field
    @property
    def is_web(self) -> bool:
        return self.mode == "web"

    @computed_field
    @property
    def is_worker(self) -> bool:
        # 'worker' включает синоним 'bot' (нормализован в normalize_mode)
        return self.mode == "worker"

    @computed_field
    @property
    def admin_ids(self) -> List[int]:
        s = (self.admin_ids_raw or "").strip()
        if not s:
            return []
        if s.startswith("[") and s.endswith("]"):
            try:
                return [int(x) for x in json.loads(s)]
            except Exception:
                pass
        parts = [p for p in s.replace(";", ",").replace(" ", ",").split(",") if p]
        if parts:
            return [int(p) for p in parts]
        try:
            return [int(s)]
        except Exception:
            return []


settings = Settings()
__all__ = ["Settings", "settings"]
