import contextlib
from typing import Annotated, AsyncGenerator

import redis.asyncio as redis
from fastapi import FastAPI, Depends, Request
from src.core.config import Settings

settings = Settings()


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 Инициализация Redis...")
    pool = redis.ConnectionPool.from_url(settings.redis_url, decode_responses=True)

    app.state.redis_client = redis.Redis(connection_pool=pool)
    print(f"✅ Redis готов к работе.")

    yield

    print(f"🛑 Закрытие соединений Redis...")
    await app.state.redis_client.aclose()
    print("👋 Соединения Redis закрыты.")


async def get_redis_client(request: Request) -> AsyncGenerator[redis.Redis, None]:
    redis_client = request.app.state.redis_client
    yield redis_client


RedisDep = Annotated[redis.Redis, Depends(get_redis_client)]
