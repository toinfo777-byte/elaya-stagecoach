from pydantic import BaseSettings

class Settings(BaseSettings):
    SAFE_MODE: bool = False
    SENTRY_DSN: str | None = None
    SQLITE_PATH: str = "stagecoach.db"
    GUARD_KEY: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
