import pathlib

from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: PostgresDsn = Field(env="postgres_url")
    redis_url: str = Field(env="redis_url")
    ttl: int = 3600
    biography_service_url: str = Field(
        ...,
        env="biography_service_url",
        description="Базовый URL микросервиса биографий (src_external), например http://localhost:8001",
    )

    temporal_host: str = Field(default="localhost:7233", env="temporal_host", description="URL Temporal сервера")
    temporal_namespace: str = Field(default="default", env="temporal_namespace")
    temporal_task_queue: str = Field(default="authors", env="temporal_task_queue", description="Имя очереди задач для workflow")

    class Config:
        env_file = pathlib.Path(__file__).parent.parent.parent / ".env"
