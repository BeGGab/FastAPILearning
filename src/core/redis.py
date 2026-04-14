import contextlib
from typing import Annotated, AsyncGenerator

import httpx
import redis.asyncio as redis
from fastapi import FastAPI, Depends, Request

from src.client.bio_author_client import AuthorServiceClient
from src.core.config import Settings

settings = Settings()


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    pool = redis.ConnectionPool.from_url(settings.redis_url, decode_responses=True)
    app.state.redis_client = redis.Redis(connection_pool=pool)

    biography_http = httpx.AsyncClient(
        base_url=str(settings.biography_service_url),
        timeout=5.0,
        follow_redirects=True,
    )
    app.state.author_service_client = AuthorServiceClient(biography_http)

    yield

    await biography_http.aclose()
    await app.state.redis_client.aclose()


async def get_redis_client(request: Request) -> AsyncGenerator[redis.Redis, None]:
    redis_client = request.app.state.redis_client
    yield redis_client


RedisDep = Annotated[redis.Redis, Depends(get_redis_client)]
