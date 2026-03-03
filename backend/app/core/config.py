from typing import ClassVar
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Configuaration
    BASE_URL: str

    # Database configuration
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    env_file_path: ClassVar[Path] = Path(__file__).parent.parent.parent / ".env.local"

    model_config = SettingsConfigDict(
        env_file=env_file_path, env_file_encoding="utf-8", case_sensitive=True
    )


# Create a single instance of the settings to be used throughout the application
settings = Settings()
