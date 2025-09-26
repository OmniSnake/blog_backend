from pydantic import ConfigDict, validator
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Конфигурация приложения"""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/blog_db"

    # JWT
    SECRET_KEY: str = "change-needed-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Security
    BCRYPT_ROUNDS: int = 12

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: str, values: dict) -> str:
        """Собираем URL для базы данных с учетом Docker окружения"""
        if v and not v.startswith("postgresql"):
            return v

        if os.getenv('DOCKER_COMPOSE'):
            return "postgresql+asyncpg://postgres:password@db:5432/blog_db"

        return v

    model_config = ConfigDict(env_file=".env")


settings = Settings()