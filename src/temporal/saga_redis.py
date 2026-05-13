"""Общие операции Redis для идемпотентности шагов саги (ключи saga:{kind}:{request_id})."""
from __future__ import annotations

import json
from typing import Any, Optional

from src.core.config import Settings
from src.core.redis import redis_client


def saga_key(kind: str, request_id: str) -> str:
    return f"saga:{kind}:{request_id}"


def _decode_redis_value(raw: Any) -> Optional[str]:
    if raw is None:
        return None
    if isinstance(raw, bytes):
        return raw.decode("utf-8")
    return str(raw)


async def saga_get_json(kind: str, request_id: str) -> Optional[dict]:
    raw = _decode_redis_value(await redis_client.get(saga_key(kind, request_id)))
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


async def saga_try_lock(kind: str, request_id: str, ttl_s: int) -> bool:
    key = saga_key(kind, request_id)
    payload = json.dumps({"status": "pending"})
    return bool(await redis_client.set(key, payload, nx=True, ex=ttl_s))


async def saga_mark_done(
    kind: str, request_id: str, author_id: str, ttl_s: int
) -> None:
    """Финальное состояние: author_id — uuid автора (для bio и для локального автора)."""
    await redis_client.set(
        saga_key(kind, request_id),
        json.dumps({"status": "done", "author_id": author_id}),
        ex=ttl_s,
    )


async def saga_release(kind: str, request_id: str) -> None:
    await redis_client.delete(saga_key(kind, request_id))


def default_saga_ttl_s() -> int:
    return Settings().ttl
