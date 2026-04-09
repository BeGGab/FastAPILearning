import uuid

import pytest

from src.routers.v1 import author as author_router
from src.schemas.author import SAuthorCreate, SAuthorRead
from src.schemas.book import SBookRead


@pytest.mark.asyncio
async def test_create_author_router_calls_service(monkeypatch) -> None:
    expected = SAuthorRead(
        id=uuid.uuid4(),
        name="Author",
        books=[SBookRead(id=uuid.uuid4(), title="Book")],
        biography_text=None,
        year_of_birth=None,
        year_of_death=None,
    )

    async def _fake_create(*_args, **_kwargs):
        return expected

    monkeypatch.setattr(author_router, "create_author_with_books", _fake_create)

    payload = SAuthorCreate(name="Author", books=[{"title": "Book"}])
    result = await author_router.create_author(
        payload=payload,
        redis=object(),
        session=object(),
        author_client=object(),
    )

    assert result.id == expected.id


@pytest.mark.asyncio
async def test_find_author_by_id_router_calls_service(monkeypatch) -> None:
    author_id = uuid.uuid4()
    expected = SAuthorRead(
        id=author_id,
        name="Author",
        books=[SBookRead(id=uuid.uuid4(), title="Book")],
        biography_text="Bio",
        year_of_birth=1980,
        year_of_death=None,
    )

    async def _fake_find(*_args, **_kwargs):
        return expected

    monkeypatch.setattr(author_router, "find_one_or_none_by_id", _fake_find)

    result = await author_router.find_author_is_id(
        author_id=author_id,
        redis=object(),
        session=object(),
        author_client=object(),
    )

    assert result.biography_text == "Bio"
