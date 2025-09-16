from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_ENV: str = "development"
    TZ: str = "Europe/Amsterdam"
    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"

    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHANNEL_ID: str

    UPLOAD_DIR: str = "/data/uploads"
    DATABASE_URL: str = "sqlite:////data/db.sqlite3"

    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    PUBLIC_BASE_URL: str = "http://localhost"

    class Config:
        env_file = ".env"

settings = Settings()
