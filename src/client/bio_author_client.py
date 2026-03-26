import uuid
import logging
from typing import Optional, Dict, Any

import httpx
from redress import (
    CircuitBreaker,
    ErrorClass,
    AsyncPolicy,
    AsyncRetry,
    default_classifier,
)
from redress.strategies import decorrelated_jitter

from src.core.config import Settings

logger = logging.getLogger(__name__)

settings = Settings()

policy = AsyncPolicy(
    retry=AsyncRetry(  # попытки соединиться с сервером и дальше его парметры
        classifier=default_classifier,  # классификатор , можно сделать кастомный более конкретный
        strategy=decorrelated_jitter(max_s=5.0),  # jitter с макс. задержкой в 5 сек
        max_attempts=5,  # макс. попыток
        deadline_s=30,  # или не дольше 30 сек
    ),
    circuit_breaker=CircuitBreaker(  # Автоматический размыкатель
        failure_threshold=5,  # разомкнуть цепь после 5 ошибок
        window_s=60.0,  # за последние 60 сек
        recovery_timeout_s=30.0,  # по пробывать снова через 30 сек
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

    async def get_author(self, author_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        try:
            response = await policy.call(
                lambda: self.client.get(f"/api/v1/biographies/{author_id}")
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.info(f"Биография для автора {author_id} не найдена (404).")
                return None
            


_author_service_client_instance: Optional[AuthorServiceClient] = None


async def get_author_client() -> AuthorServiceClient:
    global _author_service_client_instance
    if _author_service_client_instance is None:
        client = httpx.AsyncClient(
            base_url=str(settings.biography_service_url), timeout=5.0
        )
        _author_service_client_instance = AuthorServiceClient(client)
    return _author_service_client_instance
