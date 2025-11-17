from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    TG_BOT_TOKEN: str
    WEBHOOK_SECRET: str
    BASE_URL: str  # https://elaya-stagecoach-web.onrender.com


settings = Settings()
