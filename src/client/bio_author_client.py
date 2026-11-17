import uuid
import httpx
import logging

from typing import AsyncIterator, NoReturn, TypeVar

from fastapi import Depends
from pydantic import BaseModel

from src.core.config import settings
from src.exception.biography_exception import (
    BiographyAlreadyExistsError,
    BiographyBadResponseError,
    BiographyNotFoundError,
    BiographyServiceUnavailableError,
)
from src.schemas.biography import SbiographyCreate, SAuthorBioResponse
from src.utils.resilience import policy



logger = logging.getLogger(__name__)

BIOGRAPHY_URL = "api/v1/biographies"
ModelT = TypeVar("ModelT", bound=BaseModel)


class BiographyServiceClient:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        
    async def _send(self, method: str, url: str, **kwargs) -> httpx.Response:
        async def attempt() -> httpx.Response:
            response = await self.client.request(method, url, **kwargs)
            if _is_transient(response):
                _raise_unexpected(response, f"{method} {url}")
            return response
        return await policy.call(attempt)

    async def get_biography(self, author_id: uuid.UUID) -> SAuthorBioResponse:
        response = await self._send("GET", f"{BIOGRAPHY_URL}/{author_id}")
        if response.status_code == httpx.codes.NOT_FOUND:
            raise BiographyNotFoundError(author_id)
        if response.status_code != httpx.codes.OK:
            _raise_unexpected(response, "Получение биографии")
        return _parse(response, SAuthorBioResponse)

    async def create_biography_for_author(self, *, bio_data: SbiographyCreate) -> SAuthorBioResponse:
        response = await self._send("POST", f"{BIOGRAPHY_URL}/", json=bio_data.model_dump(by_alias=True, exclude_none=True))
        if response.status_code == httpx.codes.CONFLICT:
            raise BiographyAlreadyExistsError(bio_data.author_id)
        if response.status_code != httpx.codes.CREATED:
            _raise_unexpected(response, "Создание биографии")
        return _parse(response, SAuthorBioResponse)


    async def delete_biography(self, author_id: uuid.UUID) -> None:
        response = await self._send("DELETE", f"{BIOGRAPHY_URL}/{author_id}")
        if response.status_code in (httpx.codes.NO_CONTENT, httpx.codes.NOT_FOUND):
            return 
        _raise_unexpected(response, "Удаление биографии")



def _is_transient(response: httpx.Response) -> bool:
    return response.status_code in (408, 429) or response.status_code >= 500


def _raise_unexpected(response: httpx.Response, operation: str) -> NoReturn:
    preview = response.text[:500]
    if _is_transient(response):
        raise BiographyServiceUnavailableError(f"{operation}: {response.status_code} {preview}")
    raise BiographyBadResponseError(f"{operation}: неожиданный статус {response.status_code}: {preview}")


def _parse(response: httpx.Response, model: type[ModelT]) -> ModelT:
    try:
        return model.model_validate_json(response.content)
    except ValueError as exc:
        raise BiographyBadResponseError(f"Некорректный ответ сервиса биографии: {exc}") from exc


async def get_author_bio_http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(base_url=settings.biography_service_url, timeout=settings.timeout) as client:
        yield client

async def get_biography_service_client(
    client: httpx.AsyncClient = Depends(get_author_bio_http_client),
) -> BiographyServiceClient:
    return BiographyServiceClient(client)