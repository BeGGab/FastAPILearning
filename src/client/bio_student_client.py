import uuid
import httpx
import logging

from typing import Optional, Dict, Any

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
    retry=AsyncRetry(
        classifier=default_classifier,
        strategy=decorrelated_jitter(max_s=5.0),
        max_attempts=5,
        deadline_s=30,
    ),
    circuit_breaker=CircuitBreaker(
        failure_threshold=5,
        window_s=60.0,
        recovery_timeout_s=30.0,
        trip_on={ErrorClass.SERVER_ERROR, ErrorClass.CONCURRENCY, ErrorClass.TRANSIENT},
    ),
)


class StudentServiceClient:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def get_student(self, student_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        try:
            response = await policy.call(
                lambda: self.client.get(f"/api/v1/bio_students/{student_id}")
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.info(f"Студент с id {student_id} не найден (404).")
                return None
            raise


_student_service_client_instance: Optional[StudentServiceClient] = None


async def get_student_client() -> StudentServiceClient:
    global _student_service_client_instance
    if _student_service_client_instance is None:
        client = httpx.AsyncClient(
            base_url=str(settings.biography_service_url), timeout=5.0
        )
        _student_service_client_instance = StudentServiceClient(client)
    return _student_service_client_instance
