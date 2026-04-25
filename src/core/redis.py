import ujson
import redress

from typing import Optional, Any


import redis.asyncio as redis

from src.core.config import Settings

settings = Settings()

redis_client = redis.Redis.from_url(settings.redis_url)


class RedisClient:
    def __init__(self, redis: redis_client, default_ttl: int = settings.ttl):
        self.redis = redis
        self.default_ttl = default_ttl


    async def get(self, key: str) -> Optional[Any]:
        cached = await self.redis.get(key)
        if cached is None:
            return None
        return ujson.loads(cached)

    @redress.retry(max_attempts=3, deadline_s=10, strategy=redress.strategies.decorrelated_jitter(max_s=5.0))
    async def set(self, key: str, value: Any, ttl: int = None) -> None:
        ttl = ttl if ttl is not None else self.default_ttl
        await self.redis.setex(key, ttl, ujson.dumps(value))

    @redress.retry(max_attempts=3, deadline_s=10, strategy=redress.strategies.decorrelated_jitter(max_s=5.0))
    async def update(self, key: Any, value: Any, ttl: int = None) -> None:
        await self.set(key, value, ttl)

    @redress.retry(max_attempts=3, deadline_s=10, strategy=redress.strategies.decorrelated_jitter(max_s=5.0))
    async def delete(self, key: str) -> None:
        await self.redis.delete(key)


async def get_cache() -> RedisClient:
    return RedisClient(redis_client)
