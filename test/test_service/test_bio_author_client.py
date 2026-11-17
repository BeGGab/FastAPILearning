import uuid

import httpx
import pytest

from src.client.bio_author_client import BiographyServiceClient
from src.exception.biography_exception import (
    BiographyAlreadyExistsError,
    BiographyNotFoundError,
    BiographyServiceUnavailableError,
)
from src.schemas.biography import SbiographyCreate


@pytest.fixture(autouse=True)
def no_retries(monkeypatch):
    async def passthrough(call):
        return await call()

    monkeypatch.setattr("src.client.bio_author_client.policy.call", passthrough)


def make_client(status_code: int, json: dict | None = None) -> BiographyServiceClient:
    transport = httpx.MockTransport(lambda request: httpx.Response(status_code, json=json))
    return BiographyServiceClient(httpx.AsyncClient(transport=transport, base_url="http://bio"))


async def test_get_biography_returns_dto_on_200():
    client = make_client(200, {"text": "Bio", "year_of_birth": 1900, "year_of_death": 1950})
    bio = await client.get_biography(uuid.uuid4())
    assert bio.biography_text == "Bio"


async def test_get_biography_raises_not_found_on_404():
    with pytest.raises(BiographyNotFoundError):
        await make_client(404).get_biography(uuid.uuid4())


async def test_get_biography_raises_unavailable_on_503():
    with pytest.raises(BiographyServiceUnavailableError):
        await make_client(503).get_biography(uuid.uuid4())


async def test_create_raises_already_exists_on_409():
    bio = SbiographyCreate(author_id=str(uuid.uuid4()), bio_text="Bio")
    with pytest.raises(BiographyAlreadyExistsError):
        await make_client(409).create_biography_for_author(bio_data=bio)


async def test_delete_is_idempotent_on_404():
    await make_client(404).delete_biography(uuid.uuid4())