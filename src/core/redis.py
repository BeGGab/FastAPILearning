import ujson
import logging

from typing import Optional, Any


import redis.asyncio as redis

from src.core.config import Settings

logger = logging.getLogger(__name__)

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

    
    async def set(self, key: str, value: Any, ttl: int = None) -> None:
        ttl = ttl if ttl is not None else self.default_ttl
        try:
            await self.redis.setex(key, ttl, ujson.dumps(value, default=str))
        except Exception:
            logger.warning("cahce set ошибка key: %s", key, exc_info=True)
    
    async def update(self, key: Any, value: Any, ttl: int = None) -> None:
        try:
            await self.set(key, value, ttl)
        except Exception:
            logger.warning("cahce update ошибка key: %s", key, exc_info=True)

    
    async def delete(self, key: str) -> None:
        try:
            await self.redis.delete(key)
        except Exception:
            logger.warning("cahce delete ошибка key: %s", key, exc_info=True)



