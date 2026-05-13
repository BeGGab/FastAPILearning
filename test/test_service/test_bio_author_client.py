import uuid
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.client.bio_author_client import AuthorServiceClient


@pytest.mark.asyncio
async def test_get_author_returns_none_on_404() -> None:
    author_id = uuid.uuid4()
    request = httpx.Request("GET", f"http://test/api/v1/biographies/{author_id}")
    response = httpx.Response(status_code=404, request=request)

    http_client = AsyncMock()
    http_client.get = AsyncMock(return_value=response)
    service = AuthorServiceClient(http_client)

    async def passthrough(call):
        return await call()

    with patch("src.client.bio_author_client.policy.call", new=passthrough):
        result = await service.get_author(author_id)

    assert result is None


@pytest.mark.asyncio
async def test_get_author_returns_payload_on_200() -> None:
    author_id = uuid.uuid4()
    payload = {"text": "Bio", "year_of_birth": 1900, "year_of_death": 1950}
    request = httpx.Request("GET", f"http://test/api/v1/biographies/{author_id}")
    response = httpx.Response(status_code=200, request=request, json=payload)

    http_client = AsyncMock()
    http_client.get = AsyncMock(return_value=response)
    service = AuthorServiceClient(http_client)

    async def passthrough(call):
        return await call()

    with patch("src.client.bio_author_client.policy.call", new=passthrough):
        result = await service.get_author(author_id)

    assert result == payload
