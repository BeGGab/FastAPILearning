import uuid
import httpx
import logging
import ujson

from typing import Any, AsyncIterator, Dict, Optional

from fastapi import Depends

from redress import (
    CircuitBreaker,
    Classification,
    ErrorClass,
    AsyncPolicy,
    AsyncRetry
)
from redress.strategies import decorrelated_jitter

from src.exception.client_exception import BadRequestError, NotFoundError, ConflictError, ValidationError
from src.schemas.author import SAuthorCreate
from src.core.config import Settings

settings = Settings()

logger = logging.getLogger(__name__)


def _response_ujson(response: httpx.Response) -> Any:
    """Разбор JSON тела ответа через ujson (быстрее стандартного json)."""
    if not response.content:
        return None
    return ujson.loads(response.content)


def skip_log_errors(exc: BaseException) -> ErrorClass | Classification | None:
    if isinstance(exc, (ValueError, TypeError, ValidationError)):
        return ErrorClass.PERMANENT
    if isinstance(exc, (ValidationError, BadRequestError, NotFoundError, ConflictError)):
        return ErrorClass.PERMANENT

    if isinstance(exc, (httpx.HTTPStatusError, httpx.TimeoutException)):
        return ErrorClass.TRANSIENT

    return ErrorClass.UNKNOWN

policy = AsyncPolicy(
    retry=AsyncRetry(  
        classifier=skip_log_errors,
        strategy=decorrelated_jitter(max_s=5.0),
        max_attempts=5,
        deadline_s=30,
    ),
    circuit_breaker=CircuitBreaker(
        failure_threshold=5,  
        window_s=60.0,      
        recovery_timeout_s=30.0,  
        trip_on={  # какие ошибки учитываються при размыкании
            ErrorClass.SERVER_ERROR,
            ErrorClass.CONCURRENCY,
            ErrorClass.TRANSIENT,
        },
    ),
)


async def get_author_bio_http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(base_url=settings.biography_service_url, timeout=30.0) as client:
        yield client


class AuthorServiceClient:
    """Клиент для взаимодействия с внешним сервисом авторов."""

    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def create_to_author(
        self, *, author_id: uuid.UUID, author_data: SAuthorCreate
    ) -> Optional[Dict[str, Any]]:
        payload = {
            "author_id": str(author_id),
            "text": author_data.biography_text,
            "year_of_birth": author_data.year_of_birth,
            "year_of_death": author_data.year_of_death,
        }

        response = await policy.call(
            lambda: self.client.post("/api/v1/biographies/", json=payload)
        )
        if response.status_code == 201:
            return _response_ujson(response)
        logger.error(
            "Создание биографии: неожиданный статус %s: %s",
            response.status_code,
            response.text[:500],
        )
        return None

    async def get_author(self, author_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        response = await policy.call(
            lambda: self.client.get(f"/api/v1/biographies/{author_id}")
        )
        if response.status_code in (200, 206):
            return _response_ujson(response)

        if response.status_code == 404:
            logger.info(f"Биография для автора {author_id} не найдена.")
            return None

        logger.warning(
            "Получение биографии: статус %s для автора %s: %s",
            response.status_code,
            author_id,
            response.text[:500],
        )
        return None


async def get_author_service_client(
    client: httpx.AsyncClient = Depends(get_author_bio_http_client),
) -> AuthorServiceClient:
    return AuthorServiceClient(client)
