import uuid

import pytest

from src.routers.v1 import courses as courses_router
from src.schemas.courses import SCourseCreate, SCourseRead


@pytest.mark.asyncio
async def test_created_courses_router_calls_service(monkeypatch) -> None:
    expected = [SCourseRead(id=uuid.uuid4(), title="FastAPI")]

    async def _fake_create(*_args, **_kwargs):
        return expected

    monkeypatch.setattr(courses_router, "create_new_courses", _fake_create)

    result = await courses_router.created_courses(
        payload=[SCourseCreate(title="FastAPI")],
        session=object(),
    )

    assert len(result) == 1
    assert result[0].title == "FastAPI"


@pytest.mark.asyncio
async def test_get_all_courses_router_calls_service(monkeypatch) -> None:
    expected = [SCourseRead(id=uuid.uuid4(), title="Databases")]

    async def _fake_get_all(*_args, **_kwargs):
        return expected

    monkeypatch.setattr(courses_router, "find_all_courses", _fake_get_all)

    result = await courses_router.get_all_courses(session=object())

    assert result[0].title == "Databases"
