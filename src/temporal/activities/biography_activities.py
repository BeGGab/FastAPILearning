import logging
import uuid

import httpx
from temporalio import activity

from src.client.bio_author_client import AuthorServiceClient
from src.core.config import Settings
from src.schemas.author import SAuthorCreate
from src.temporal.models import CreateBiographyInput, DeleteBiographyInput
from src.temporal.saga_redis import (
    saga_get_json,
    saga_mark_done,
    saga_release,
    saga_try_lock,
)

logger = logging.getLogger(__name__)

_SAGA_KIND_BIO = "bio"


@activity.defn(name="create_biography_activity")
async def create_biography_activity(inp: CreateBiographyInput) -> None:
    settings = Settings()
    ttl_s = settings.ttl

    state = await saga_get_json(_SAGA_KIND_BIO, inp.request_id)
    if state and state.get("status") == "done":
        logger.info(
            "create_biography_activity: идемпотентный кэш hit request_id=%s",
            inp.request_id,
        )
        return

    acquired = await saga_try_lock(_SAGA_KIND_BIO, inp.request_id, ttl_s)
    if not acquired:
        state = await saga_get_json(_SAGA_KIND_BIO, inp.request_id)
        if state and state.get("status") == "done":
            return
        raise RuntimeError(
            f"Сага биографии {inp.request_id} не может быть взята"
        )

    async with httpx.AsyncClient(
        base_url=settings.biography_service_url, timeout=30.0
    ) as http:
        client = AuthorServiceClient(http)
        aid = uuid.UUID(inp.author_id)

        existing = await client.get_author(author_id=aid)
        if existing is not None:
            await saga_mark_done(_SAGA_KIND_BIO, inp.request_id, inp.author_id, ttl_s)
            logger.info(
                "create_biography_activity: биография уже существует author_id=%s",
                inp.author_id,
            )
            return

        author_create = SAuthorCreate(
            name=inp.author_name,
            books=[],
            biography_text=inp.biography_text,
            year_of_birth=inp.year_of_birth,
            year_of_death=inp.year_of_death,
        )

        try:
            result = await client.create_to_author(
                author_id=aid,
                author_data=author_create,
            )
        except Exception:
            await saga_release(_SAGA_KIND_BIO, inp.request_id)
            raise

        if result is None:
            await saga_release(_SAGA_KIND_BIO, inp.request_id)
            raise RuntimeError("Сервис биографий вернул no данных после POST")

    await saga_mark_done(_SAGA_KIND_BIO, inp.request_id, inp.author_id, ttl_s)


@activity.defn(name="delete_biography_activity")
async def delete_biography_activity(inp: DeleteBiographyInput) -> None:
    settings = Settings()
    await saga_release(_SAGA_KIND_BIO, inp.request_id)

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
