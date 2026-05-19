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


class SagaRedis:
    def __init__(self, redis: redis_client, settings: Settings, default_ttl: int = settings.ttl):
        self.redis = redis
        self.settings = settings
        self.default_ttl = default_ttl

    def saga_key(self, kind: str, request_id: str) -> str:
        return f"saga:{kind}:{request_id}"
        
    async def _decode_redis_value(self, raw: Any) -> Optional[dict]:
        if raw is None:
            return None
        if isinstance(raw, bytes):
            return ujson.loads(raw)
        return ujson.loads(raw)

    async def saga_mark_done(self,
        kind: str, request_id: str, author_id: str, ttl_s: int
    ) -> None:
        await self.redis.set(self.saga_key(kind, request_id), ujson.dumps({"status": "done", "author_id": author_id}), ex=ttl_s)


    async def saga_get_json(self, kind: str, request_id: str) -> Optional[dict]:
        raw = await self.redis.get(self.saga_key(kind, request_id))
        if not raw:
            return None
        try:
            return await self._decode_redis_value(raw)
        except (ujson.JSONDecodeError, TypeError, ValueError):
            return None

    async def saga_try_lock(self, kind: str, request_id: str, ttl_s: int) -> bool:
        key = self.saga_key(kind, request_id)
        payload = ujson.dumps({"status": "pending"})
        return bool(await self.redis.set(key, payload, nx=True, ex=ttl_s))

    

    async def saga_release(self, kind: str, request_id: str) -> None:
        await self.redis.delete(self.saga_key(kind, request_id))

