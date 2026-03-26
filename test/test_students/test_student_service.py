import json
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.schemas.student import SStudentRead
from src.service.student import find_one_with_id


def _cached_student(student_id: uuid.UUID) -> dict:
    return {
        "id": str(student_id),
        "name": "Cached Student",
        "courses": [{"id": str(uuid.uuid4()), "title": "Python"}],
        "email": None,
        "phone_number": None,
        "bio_text": None,
        "year_of_enrollment": None,
        "year_of_graduation": None,
    }


@pytest.mark.asyncio
async def test_find_student_cache_hit_enriches_and_updates_cache() -> None:
    student_id = uuid.uuid4()
    redis = SimpleNamespace(
        get=AsyncMock(return_value=json.dumps(_cached_student(student_id))),
        setex=AsyncMock(),
    )
    student_client = SimpleNamespace(
        get_student=AsyncMock(
            return_value={
                "email": "s@example.com",
                "phone_number": "+79990001122",
                "text": "Bio",
            }
        )
    )

    result = await find_one_with_id(
        session=object(),
        redis=redis,
        student_id=student_id,
        student_client=student_client,
    )

    assert isinstance(result, SStudentRead)
    assert result.id == student_id
    assert result.email == "s@example.com"
    redis.setex.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_student_cache_hit_without_bio_keeps_cached() -> None:
    student_id = uuid.uuid4()
    redis = SimpleNamespace(
        get=AsyncMock(return_value=json.dumps(_cached_student(student_id))),
        setex=AsyncMock(),
    )
    student_client = SimpleNamespace(get_student=AsyncMock(return_value=None))

    result = await find_one_with_id(
        session=object(),
        redis=redis,
        student_id=student_id,
        student_client=student_client,
    )

    assert result.id == student_id
    assert result.email is None
    redis.setex.assert_not_awaited()
