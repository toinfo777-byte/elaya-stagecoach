from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # общая конфигурация чтения .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",        # лишние переменные просто игнорируем
    )

    # базовые флаги окружения
    ENV: str = "local"
    MODE: str = "web"
    LOG_LEVEL: str = "INFO"

    # --- Telegram токены ---
    # главный токен тренера (то, что мы используем в app/bot/main.py)
    TG_BOT_TOKEN: str

    # запасные варианты, если где-то в коде используются другие имена
    TELEGRAM_TOKEN: str | None = None
    BOT_TOKEN: str | None = None

    # --- чаты и инфраструктура (делаю опциональными, чтобы ничего не падало) ---
    ADMIN_ALERT_CHAT_ID: int | None = None
    HQ_CHAT_ID: int | None = None

    WEBHOOK_SECRET: str | None = None
    SENTRY_DSN: str | None = None
    DB_URL: str | None = None
    SQLITE_PATH: str | None = None
    BUILD_MARK: str | None = None


settings = Settings()
