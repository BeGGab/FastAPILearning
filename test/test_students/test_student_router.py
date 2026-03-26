import uuid

import pytest

from src.routers.v1 import student as student_router
from src.schemas.courses import SCourseRead
from src.schemas.student import SStudentCreate, SStudentRead


@pytest.mark.asyncio
async def test_created_student_router_calls_service(monkeypatch) -> None:
    expected = SStudentRead(
        id=uuid.uuid4(),
        name="Student",
        courses=[SCourseRead(id=uuid.uuid4(), title="Python")],
        email=None,
        phone_number=None,
        bio_text=None,
        year_of_enrollment=None,
        year_of_graduation=None,
    )

    async def _fake_add(*_args, **_kwargs):
        return expected

    monkeypatch.setattr(student_router, "add_student", _fake_add)

    payload = SStudentCreate(name="Student", courses=[{"title": "Python"}])
    result = await student_router.created_student(
        payload=payload,
        redis=object(),
        session=object(),
        student_client=object(),
    )

    assert result.id == expected.id


@pytest.mark.asyncio
async def test_get_student_by_id_router_calls_service(monkeypatch) -> None:
    student_id = uuid.uuid4()
    expected = SStudentRead(
        id=student_id,
        name="Student",
        courses=[SCourseRead(id=uuid.uuid4(), title="Python")],
        email="s@example.com",
        phone_number="+79990001122",
        bio_text="Bio",
        year_of_enrollment=None,
        year_of_graduation=None,
    )

    async def _fake_find(*_args, **_kwargs):
        return expected

    monkeypatch.setattr(student_router, "find_one_with_id", _fake_find)

    result = await student_router.get_student_by_id(
        student_id=student_id,
        redis=object(),
        session=object(),
        student_client=object(),
    )

    assert result.email == "s@example.com"
