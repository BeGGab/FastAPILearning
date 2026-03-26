import json
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.schemas.author import SAuthorRead
from src.schemas.book import SBookRead
from src.service.author import find_one_or_none_by_id


def _cached_author(author_id: uuid.UUID) -> dict:
    return {
        "id": str(author_id),
        "name": "Cached Author",
        "books": [{"id": str(uuid.uuid4()), "title": "Book"}],
        "biography_text": None,
        "year_of_birth": None,
        "year_of_death": None,
    }


@pytest.mark.asyncio
async def test_find_author_cache_hit_enriches_and_updates_cache() -> None:
    author_id = uuid.uuid4()
    redis = SimpleNamespace(
        get=AsyncMock(return_value=json.dumps(_cached_author(author_id))),
        setex=AsyncMock(),
    )
    author_client = SimpleNamespace(
        get_author=AsyncMock(
            return_value={"text": "Bio", "year_of_birth": 1980, "year_of_death": 2020}
        )
    )

    result = await find_one_or_none_by_id(
        session=object(),
        author_id=author_id,
        redis=redis,
        author_client=author_client,
    )

    assert isinstance(result, SAuthorRead)
    assert result.id == author_id
    assert result.biography_text == "Bio"
    redis.setex.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_author_cache_hit_without_bio_keeps_cached() -> None:
    author_id = uuid.uuid4()
    redis = SimpleNamespace(
        get=AsyncMock(return_value=json.dumps(_cached_author(author_id))),
        setex=AsyncMock(),
    )
    author_client = SimpleNamespace(get_author=AsyncMock(return_value=None))

    result = await find_one_or_none_by_id(
        session=object(),
        author_id=author_id,
        redis=redis,
        author_client=author_client,
    )

    assert result.id == author_id
    assert result.biography_text is None
    redis.setex.assert_not_awaited()
