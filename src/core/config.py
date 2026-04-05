import os

from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: PostgresDsn = Field(env="postgres_url")
    redis_url: str = Field(env="redis_url")
    biography_service_url: str = Field(
        ...,
        env="biography_service_url",
        description="Базовый URL микросервиса биографий (src_external), например http://localhost:8001",
    )

    class Config:
        env_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
        )
