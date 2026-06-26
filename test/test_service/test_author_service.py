import uuid
from unittest.mock import AsyncMock, patch

import pytest

from src.schemas.author import (
    CompensationResult,
    CreateAuthorSagaResult,
    SAuthorCreate,
    SAuthorRead,
    SAuthorUpdate,
)
from src.exception.client_exception import NotFoundError
from src.exception.server_exception import InternalServerError


async def _seed_author(author_repository, db_session, name: str = "Test Author"):
    author, _ = await author_repository.created(
        author_data=SAuthorCreate(name=name, books=[{"title": "Test Book"}]),
    )
    await db_session.flush()
    return author


@pytest.mark.asyncio
async def test_create_author_with_books_success(
    author_service, author_repository, db_session, mock_author_client
):
    author = await _seed_author(author_repository, db_session, name="New Author")
    payload = SAuthorCreate(
        name="New Author",
        books=[{"title": "Book 1"}],
        biography_text="Bio",
        year_of_birth=1900,
        year_of_death=1950,
    )
    mock_author_client.get_biography.return_value = {
        "text": "Bio",
        "year_of_birth": 1900,
        "year_of_death": 1950,
    }
    saga_result = CreateAuthorSagaResult(
        author_id=str(author.id),
        biography_created=True,
        compensated_author=CompensationResult(attempted=False, success=False),
        compensated_biography=CompensationResult(attempted=False, success=False),
    )

    with patch(
        "src.service.author.run_create_author_saga",
        new_callable=AsyncMock,
    ) as mock_saga:
        mock_saga.return_value = saga_result
        result = await author_service.create_author_with_books(payload, request_id="req-1")

    assert result.id == author.id
    assert result.biography_text == "Bio"
    mock_saga.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_author_with_books_raises_when_saga_fails(author_service):
    payload = SAuthorCreate(
        name="Broken Author",
        books=[{"title": "Book 1"}],
        biography_text="Bio",
        year_of_birth=1900,
        year_of_death=1950,
    )

    with patch(
        "src.service.author.run_create_author_saga",
        new_callable=AsyncMock,
        side_effect=RuntimeError("saga failed"),
    ):
        with pytest.raises(InternalServerError):
            await author_service.create_author_with_books(payload)


@pytest.mark.asyncio
async def test_find_one_or_none_by_id_returns_from_cache(
    author_service, author_repository, db_session, cache_service, mock_author_client
):
    author = await _seed_author(author_repository, db_session, name="Cached Author")
    cached = SAuthorRead.from_orm(author)
    await cache_service.set(f"author:{author.id}", cached.to_cache())

    result = await author_service.find_one_or_none_by_id(author.id)

    assert result.id == author.id
    assert result.name == "Cached Author"
    mock_author_client.get_biography.assert_not_called()


@pytest.mark.asyncio
async def test_find_one_or_none_by_id_loads_from_db_and_enriches_bio(
    author_service, author_repository, db_session, mock_author_client
):
    author = await _seed_author(author_repository, db_session)
    mock_author_client.get_biography.return_value = {
        "text": "Updated bio",
        "year_of_birth": 1901,
        "year_of_death": 1955,
    }

    result = await author_service.find_one_or_none_by_id(author.id)

    assert result.biography_text == "Updated bio"
    assert result.year_of_birth == 1901
    mock_author_client.get_biography.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_one_or_none_by_id_raises_not_found_when_missing_in_db(
    author_service,
):
    with pytest.raises(NotFoundError):
        await author_service.find_one_or_none_by_id(uuid.uuid4())


@pytest.mark.asyncio
async def test_find_all_authors_returns_from_cache(
    author_service, author_repository, db_session, cache_service
):
    author = await _seed_author(author_repository, db_session, name="Cached List Author")
    cached = SAuthorRead.from_orm(author)
    await cache_service.set("authors:({}, 0, 100)", [cached.to_cache()])

    result = await author_service.find_all_authors()

    assert len(result) == 1
    assert result[0].id == author.id


@pytest.mark.asyncio
async def test_find_all_authors_raises_not_found_when_repo_empty(author_service):
    with pytest.raises(NotFoundError):
        await author_service.find_all_authors()


@pytest.mark.asyncio
async def test_find_all_authors_loads_from_db(
    author_service, author_repository, db_session
):
    author = await _seed_author(author_repository, db_session, name="Db Author")

    result = await author_service.find_all_authors()

    assert len(result) == 1
    assert result[0].id == author.id


@pytest.mark.asyncio
async def test_update_author_with_books_success_updates_cache(
    author_service, author_repository, db_session, cache_service
):
    author = await _seed_author(author_repository, db_session, name="Original")
    payload = SAuthorUpdate(name="Updated Author")

    result = await author_service.update_author_with_books(author.id, payload)

    assert result.name == "Updated Author"
    cached = await cache_service.get(f"author:{author.id}")
    assert cached is not None
    assert cached["name"] == "Updated Author"


@pytest.mark.asyncio
async def test_delete_author_success_removes_cache_and_entity(
    author_service, author_repository, db_session, cache_service
):
    author = await _seed_author(author_repository, db_session)
    await cache_service.set(f"author:{author.id}", SAuthorRead.from_orm(author).to_cache())

    await author_service.delete_author(author.id)
    await db_session.flush()

    assert await cache_service.get(f"author:{author.id}") is None
    assert await author_repository.get_id(id=author.id) is None
