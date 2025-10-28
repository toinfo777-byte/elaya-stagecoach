from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    MODE: str = Field("web")           # 'web' | 'polling'
    BOT_TOKEN: str = ""                # у web можно оставить пустым
    ENV: str = "staging"
    TZ_DEFAULT: str = "Europe/Moscow"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
