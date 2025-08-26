from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Глобальные настройки сервиса.

    Источники:
    - переменные окружения,
    - .env.
    """
    APP_NAME: str = "spimex-microservice"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = Field(..., description="SQLAlchemy async URL")
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TZ: str = "Europe/Moscow"
    CACHE_RESET_HOUR: int = 14
    CACHE_RESET_MINUTE: int = 11
    MAX_LAST_DATES: int = 60
    DEFAULT_LAST_DATES: int = 5
    MAX_DYNAMICS_SPAN_DAYS: int = 366

    class Config:
        env_file = ".env"


settings = Settings()
