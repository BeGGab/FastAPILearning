import uuid
import httpx
import logging

from typing import Any, AsyncIterator, Dict, Optional

from fastapi import Depends

from src.exception.client_exception import NotFoundError
from src.schemas.author import SAuthorCreate
from src.core.config import Settings
from src.utils.resilience import _response_json, _raise_logical_error
from src.utils.resilience import policy

settings = Settings()

logger = logging.getLogger(__name__)


async def get_author_bio_http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(base_url=settings.biography_service_url, timeout=30.0) as client:
        yield client


class BiographyServiceClient:

    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        
    async def get_biography(self, author_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        async def _send_get_request() -> httpx.Response:
            response = await self.client.get(f"/api/v1/biographies/{author_id}")
            if response.status_code == 404:
                return response
            if response.status_code >= 400:
                _raise_logical_error(response, "Получение биографии")
            return response

        response = await policy.call(_send_get_request)
        if response.status_code in (200, 206):
            return _response_json(response)
        if response.status_code == 404:
            logger.info(
                "Получение биографии: биография автора %s отсутствует",
                author_id,
            )
            raise NotFoundError(detail=f"Биография автора {author_id} не найдена")

        logger.warning(
            "Получение биографии: статус %s для автора %s: %s",
            response.status_code,
            author_id,
            response.text[:500],
        )
        return response.status_code

    async def create_to_author(
        self, *, author_id: uuid.UUID, author_data: SAuthorCreate
    ) -> Optional[Dict[str, Any]]:
        payload = {
            "author_id": str(author_id),
            "text": author_data.biography_text,
            "year_of_birth": author_data.year_of_birth,
            "year_of_death": author_data.year_of_death,
        }

        async def _send_create_request() -> httpx.Response:
            response = await self.client.post("/api/v1/biographies/", json=payload)
            if response.status_code >= 400:
                _raise_logical_error(response, "Создание биографии")
            return response

        response = await policy.call(_send_create_request)
        if response.status_code == 201:
            return _response_json(response)
        logger.error(
            "Создание биографии: неожиданный статус %s: %s",
            response.status_code,
            response.text[:500],
        )
        return response.status_code

    

async def get_biography_service_client(
    client: httpx.AsyncClient = Depends(get_author_bio_http_client),
) -> BiographyServiceClient:
    return BiographyServiceClient(client)
