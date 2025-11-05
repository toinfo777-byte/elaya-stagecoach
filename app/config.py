from __future__ import annotations

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Основные переменные окружения для всех сервисов Элайи."""

    # ─── Общие ──────────────────────────────────────────────
    env: str = os.getenv("ENV", "staging")
    mode: str = os.getenv("MODE", "manual")
    build_mark: str = os.getenv("BUILD_MARK", os.getenv("RENDER_GIT_COMMIT", "manual"))

    # ─── Telegram ──────────────────────────────────────────
    telegram_token: str | None = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")
    hq_chat_id: str | None = os.getenv("HQ_CHAT_ID") or os.getenv("TG_HQ_CHAT_ID")
    admin_alert_chat_id: str | None = os.getenv("ADMIN_ALERT_CHAT_ID") or os.getenv("TG_REPORT_CHAT_ID")

    # ─── Render system vars ─────────────────────────────────
    render_service: str | None = os.getenv("RENDER_SERVICE_NAME")
    render_instance: str | None = os.getenv("RENDER_INSTANCE_ID")
    render_region: str | None = os.getenv("RENDER_REGION")
    render_git_commit: str | None = os.getenv("RENDER_GIT_COMMIT")
    render_api_key: str | None = os.getenv("RENDER_API_KEY")
    render_service_id: str | None = os.getenv("RENDER_SERVICE_ID")

    # ─── Webhook flags ──────────────────────────────────────
    disable_tg: bool = os.getenv("DISABLE_TG", "0") == "1"
    send_startup_banner: bool = os.getenv("SEND_STARTUP_BANNER", "0") == "1"

    # ─── Доп. информация ────────────────────────────────────
    service_name: str | None = os.getenv("SERVICE_NAME", "")
    project_root: str = os.getcwd()

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
