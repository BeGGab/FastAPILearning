import uuid

import pytest
import ujson
from unittest.mock import AsyncMock, Mock

from src.models.author import Author
from src.models.books import Book
from src.schemas.author import SAuthorCreate, SAuthorRead, SAuthorUpdate
from src.service.author import AuthorService
from src.exception.client_exception import NotFoundError
from src.exception.server_exception import InternalServerError


def _make_author(name: str = "Test Author") -> Author:
    author = Author(id=uuid.uuid4(), name=name)
    book = Book(id=uuid.uuid4(), title="Test Book", author_id=author.id)
    author.books = [book]
    return author


@pytest.fixture
def service_deps():
    session = Mock()
    session.add = Mock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()

    repository = Mock()
    repository.created = AsyncMock()
    repository.get_id = AsyncMock()
    repository.get_all = AsyncMock()
    repository.update = AsyncMock()
    repository.apply_biography_to_author_data = Mock()

    cache = AsyncMock()
    cache.get = AsyncMock()
    cache.set = AsyncMock()
    cache.delete = AsyncMock()

    author_client = AsyncMock()
    author_client.create_to_author = AsyncMock()
    author_client.get_author = AsyncMock()

    service = AuthorService(
        session=session,
        repository=repository,
        cache=cache,
        author_client=author_client,
    )
    return service, session, repository, cache, author_client


@pytest.mark.asyncio
async def test_create_author_with_books_success(service_deps):
    service, session, repository, cache, author_client = service_deps
    author = _make_author()
    payload = SAuthorCreate(
        name="New Author",
        books=[{"title": "Book 1"}],
        biography_text="Bio",
        year_of_birth=1900,
        year_of_death=1950,
    )
    enriched = SAuthorRead.model_validate(author, from_attributes=True).model_copy(
        update={"biography_text": "Bio", "year_of_birth": 1900, "year_of_death": 1950}
    )

    repository.created.return_value = (author, author.books)
    author_client.create_to_author.return_value = {
        "text": "Bio",
        "year_of_birth": 1900,
        "year_of_death": 1950,
    }
    repository.apply_biography_to_author_data.return_value = enriched

    result = await service.create_author_with_books(payload)

    assert result == enriched
    session.add.assert_called_once_with(author)
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(author, ["books"])
    cache.set.assert_awaited_once()
    author_client.create_to_author.assert_awaited_once_with(author_id=author.id, author_data=payload)


@pytest.mark.asyncio
async def test_create_author_with_books_raises_when_repo_returns_none(service_deps):
    service, _session, repository, _cache, _author_client = service_deps
    payload = SAuthorCreate(
        name="Broken Author",
        books=[{"title": "Book 1"}],
        biography_text="Bio",
        year_of_birth=1900,
        year_of_death=1950,
    )
    repository.created.return_value = (None, [])

    with pytest.raises(InternalServerError):
        await service.create_author_with_books(payload)


@pytest.mark.asyncio
async def test_find_one_or_none_by_id_returns_cached_and_refreshes_cache_when_changed(service_deps):
    service, _session, repository, cache, author_client = service_deps
    author_id = uuid.uuid4()
    cached = SAuthorRead(
        id=author_id,
        name="Cached Author",
        books=[{"id": uuid.uuid4(), "title": "Book 1"}],
        biography_text=None,
        year_of_birth=None,
        year_of_death=None,
    )
    enriched = cached.model_copy(update={"biography_text": "Updated bio", "year_of_birth": 1901})

    cache.get.return_value = cached.model_dump_json()
    author_client.get_author.return_value = {"text": "Updated bio", "year_of_birth": 1901, "year_of_death": None}
    repository.apply_biography_to_author_data.return_value = enriched

    result = await service.find_one_or_none_by_id(author_id)

    assert result == enriched
    repository.get_id.assert_not_called()
    cache.set.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_one_or_none_by_id_raises_not_found_when_missing_in_db(service_deps):
    service, _session, repository, cache, author_client = service_deps
    author_id = uuid.uuid4()
    cache.get.return_value = None
    repository.get_id.return_value = None
    author_client.get_author.return_value = None
    repository.apply_biography_to_author_data.return_value = None

    with pytest.raises(NotFoundError):
        await service.find_one_or_none_by_id(author_id)


@pytest.mark.asyncio
async def test_find_all_authors_returns_from_cache(service_deps):
    service, _session, repository, cache, _author_client = service_deps
    author = SAuthorRead(
        id=uuid.uuid4(),
        name="Cached List Author",
        books=[{"id": uuid.uuid4(), "title": "Book 1"}],
        biography_text=None,
        year_of_birth=None,
        year_of_death=None,
    )
    cache.get.return_value = ujson.dumps([author.model_dump_json()])

    result = await service.find_all_authors()

    assert len(result) == 1
    assert result[0].id == author.id
    repository.get_all.assert_not_called()


@pytest.mark.asyncio
async def test_find_all_authors_raises_not_found_when_repo_empty(service_deps):
    service, _session, repository, cache, _author_client = service_deps
    cache.get.return_value = None
    repository.get_all.return_value = []

    with pytest.raises(NotFoundError):
        await service.find_all_authors()


@pytest.mark.asyncio
async def test_update_author_with_books_success_updates_cache(service_deps):
    service, session, repository, cache, _author_client = service_deps
    author = _make_author("Updated")
    payload = SAuthorUpdate(name="Updated Author")
    repository.update.return_value = author

    result = await service.update_author_with_books(author.id, payload)

    assert result.id == author.id
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(author, ["books"])
    cache.set.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_author_success_removes_cache_and_entity(service_deps):
    service, session, repository, cache, _author_client = service_deps
    author = _make_author()
    repository.get_id.return_value = author

    await service.delete_author(author.id)

    cache.delete.assert_awaited_once_with(f"author:{author.id}")
    session.delete.assert_awaited_once_with(author)
