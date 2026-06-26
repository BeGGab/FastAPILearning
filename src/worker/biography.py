import logging
import uuid

import httpx
from temporalio import activity

from src.client.bio_author_client import BiographyServiceClient
from src.core.config import settings
from src.core.redis import SagaRedis, redis_client
from src.exception.client_exception import NotFoundError
from src.schemas.biography import CreateBiographyInput, DeleteBiographyInput, SbiographyCreate

logger = logging.getLogger(__name__)

_SAGA_KIND_BIO = "bio"


async def create_biography(inp: CreateBiographyInput) -> None:
    ttl_s = settings.ttl
    redis = SagaRedis(redis_client, settings, ttl_s)

    state = await redis.saga_get_json(_SAGA_KIND_BIO, inp.request_id)
    if state and state.get("status") == "done":
        logger.info(
            "create_biography_activity: идемпотентный кэш hit request_id=%s",
            inp.request_id,
        )
        return

    lock_acquired = await redis.saga_try_lock(_SAGA_KIND_BIO, inp.request_id, ttl_s)
    if not lock_acquired:
        state = await redis.saga_get_json(_SAGA_KIND_BIO, inp.request_id)
        if state and state.get("status") == "done":
            return
        raise RuntimeError(
            f"Сага биографии {inp.request_id} занята; повторите activity"
        )

    try:
        async with httpx.AsyncClient(
            base_url=settings.biography_service_url, timeout=30.0
        ) as http:
            client = BiographyServiceClient(http)
            aid = uuid.UUID(inp.author_id)

            try:
                existing = await client.get_biography(author_id=aid)
            except NotFoundError:
                existing = None

            if existing is not None:
                logger.info(
                    "create_biography: биография уже существует author_id=%s",
                    inp.author_id,
                )
            else:
                result = await client.create_to_author(
                    bio_data=SbiographyCreate(
                        author_id=str(aid),
                        bio_text=inp.biography_text,
                        year_of_birth=inp.year_of_birth,
                        year_of_death=inp.year_of_death,
                    ),
                )
                if not isinstance(result, dict):
                    raise RuntimeError("Сервис биографий вернул None после POST")
    except Exception:
        await redis.saga_release(_SAGA_KIND_BIO, inp.request_id)
        raise

    await redis.saga_mark_done(_SAGA_KIND_BIO, inp.request_id, inp.author_id, ttl_s)


async def delete_biography(inp: DeleteBiographyInput) -> None:
    ttl_s = settings.ttl
    redis = SagaRedis(redis_client, settings, ttl_s)
    await redis.saga_release(_SAGA_KIND_BIO, inp.request_id)

    url = f"/api/v1/biographies/{inp.author_id}"
    async with httpx.AsyncClient(
        base_url=settings.biography_service_url, timeout=30.0
    ) as http:
        response = await http.delete(url)

    if response.status_code in (204, 404):
        return

    if response.status_code >= 400:
        raise RuntimeError(
            f"Удаление биографии failed: {response.status_code} {response.text[:500]}"
        )
