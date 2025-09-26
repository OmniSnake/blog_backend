from pydantic import ConfigDict
from pydantic_settings import BaseSettings


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

    model_config = ConfigDict(env_file=".env")


settings = Settings()