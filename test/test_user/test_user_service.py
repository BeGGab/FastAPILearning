import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.service.user import find_one_or_none_with_profile


@pytest.mark.asyncio
async def test_find_one_with_profile_cache_hit_enriches_and_updates_cache(
    user_id,
    cached_user_payload,
    bio_user_payload,
) -> None:
    redis = SimpleNamespace(
        get=AsyncMock(return_value=json.dumps(cached_user_payload)),
        setex=AsyncMock(),
    )
    user_client = SimpleNamespace(get_user=AsyncMock(return_value=bio_user_payload))

    result = await find_one_or_none_with_profile(
        session=object(),
        redis=redis,
        user_client=user_client,
        id=user_id,
    )

    assert result.id == user_id
    assert result.bio_text == bio_user_payload["text"]
    assert result.year_of_birth == bio_user_payload["year_of_birth"]
    redis.setex.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_one_with_profile_cache_hit_without_bio_keeps_cached_data(
    user_id,
    cached_user_payload,
) -> None:
    redis = SimpleNamespace(
        get=AsyncMock(return_value=json.dumps(cached_user_payload)),
        setex=AsyncMock(),
    )
    user_client = SimpleNamespace(get_user=AsyncMock(return_value=None))

    result = await find_one_or_none_with_profile(
        session=object(),
        redis=redis,
        user_client=user_client,
        id=user_id,
    )

    assert result.id == user_id
    assert result.bio_text is None
    assert result.year_of_birth is None
    redis.setex.assert_not_awaited()
