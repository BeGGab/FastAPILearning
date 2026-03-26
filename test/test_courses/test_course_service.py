from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
import uuid

from src.schemas.courses import SCourseCreate
from src.service.courses import find_all_courses, update_courses


@pytest.mark.asyncio
async def test_find_all_courses_returns_empty_list_when_none(monkeypatch) -> None:
    fake_repo = SimpleNamespace(get_all=AsyncMock(return_value=[]))
    monkeypatch.setattr("src.service.courses.rep", lambda _session: fake_repo)

    result = await find_all_courses(session=object())
    assert result == []


@pytest.mark.asyncio
async def test_update_courses_maps_repository_result(monkeypatch) -> None:
    fake_repo = SimpleNamespace(
        update=AsyncMock(
            return_value=[SimpleNamespace(id=uuid.uuid4(), title="FastAPI")]
        )
    )
    monkeypatch.setattr("src.service.courses.rep", lambda _session: fake_repo)

    result = await update_courses(
        session=object(),
        course_data=[SCourseCreate(title="FastAPI")],
    )

    assert len(result) == 1
    assert result[0].title == "FastAPI"
