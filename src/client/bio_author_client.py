import uuid
import httpx
import logging

from typing import Any, Dict, Optional
from typing import Annotated, AsyncGenerator

from fastapi import Depends, Request

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

logger = logging.getLogger(__name__)


def my_classifier(exc: BaseException) -> ErrorClass | Classification | None:
    if isinstance(exc, (ValueError, TypeError, ValidationError)):
        return ErrorClass.PERMANENT
    if isinstance(exc, (ValidationError, BadRequestError, NotFoundError, ConflictError)):
        return ErrorClass.PERMANENT

    if isinstance(exc, (httpx.HTTPStatusError, httpx.TimeoutException)):
        return ErrorClass.TRANSIENT

    return ErrorClass.UNKNOWN

policy = AsyncPolicy(
    retry=AsyncRetry(  
        classifier=my_classifier,
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
        try:
            response = await policy.call(
                lambda: self.client.post("/api/v1/biographies/", json=payload)
            )
            if response.status_code == 201:
                return response.json()
            else:
                logger.error(f"Ошибка при создании биографии для автора: {response.status_code} {response.text}")
                raise Exception(f"Ошибка при создании биографии для автора: {response.status_code} {response.text}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Ошибка при создании биографии для автора: {e.response.status_code} {e.response.text}")
            raise Exception(f"Ошибка при создании биографии для автора: {e.response.status_code} {e.response.text}")

    async def get_author(self, author_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        try:
            response = await policy.call(
                lambda: self.client.get(f"/api/v1/biographies/{author_id}")
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Ошибка при получении биографии для автора {author_id}: {response.status_code} {response.text}")
                raise Exception(f"Ошибка при получении биографии для автора {author_id}: {response.status_code} {response.text}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.info(f"Биография для автора {author_id} не найдена.")
                return None
            logger.error(f"Ошибка при получении биографии для автора {author_id}: {e.response.status_code} {e.response.text}")
            raise Exception(f"Ошибка при получении биографии для автора {author_id}: {e.response.status_code} {e.response.text}")


async def get_author_service_client(request: Request) -> AsyncGenerator[AuthorServiceClient, None]:
    yield request.app.state.author_service_client
    

AuthorClientDep = Annotated[AuthorServiceClient, Depends(get_author_service_client)]