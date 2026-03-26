from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.repositories.course import CourseRepository
from src.schemas.courses import SCourseCreate


@pytest.mark.asyncio
async def test_course_repository_update_returns_existing_plus_new() -> None:
    repo = CourseRepository(session=SimpleNamespace())
    existing = [SimpleNamespace(title="Python")]
    new_created = [SimpleNamespace(title="FastAPI")]
    course_data = [SCourseCreate(title="Python"), SCourseCreate(title="FastAPI")]

    repo.find = AsyncMock(return_value=existing)  # type: ignore[method-assign]
    repo.create = AsyncMock(return_value=new_created)  # type: ignore[method-assign]

    result = await repo.update(course_data)

    assert [c.title for c in result] == ["Python", "FastAPI"]
    repo.find.assert_awaited_once()
    repo.create.assert_awaited_once()
