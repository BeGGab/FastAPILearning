import uuid

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport

from src.core.dependencies import get_author_service
from src.exception.client_exception import NotFoundError
from src.schemas.author import SAuthorRead


def _author_read(author_id: uuid.UUID | None = None) -> SAuthorRead:
    author_id = author_id or uuid.uuid4()
    return SAuthorRead(
        id=author_id,
        name="Router Author",
        books=[{"id": uuid.uuid4(), "title": "Book 1"}],
        biography_text=None,
        year_of_birth=None,
        year_of_death=None,
    )


@pytest.fixture
def mock_author_service():
    service = AsyncMock()
    service.create_author_with_books = AsyncMock()
    service.find_all_authors = AsyncMock()
    service.find_one_or_none_by_id = AsyncMock()
    service.update_author_with_books = AsyncMock()
    service.delete_author = AsyncMock()
    return service


@pytest.fixture
def app_with_mocked_author_service(app, mock_author_service):
    app.dependency_overrides[get_author_service] = lambda: mock_author_service
    yield app
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app_with_mocked_author_service):
    transport = ASGITransport(app=app_with_mocked_author_service)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client


@pytest.mark.asyncio
async def test_create_author_returns_201_and_payload(client, mock_author_service):
    author = _author_read()
    mock_author_service.create_author_with_books.return_value = author

    response = await client.post(
        "/api/v1/authors_books/",
        json={
            "name": "New Author",
            "books": [{"title": "Book 1"}],
            "biography_text": "Bio",
            "year_of_birth": 1900,
            "year_of_death": 1950,
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == str(author.id)
    mock_author_service.create_author_with_books.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_all_returns_200_and_list(client, mock_author_service):
    authors = [_author_read(), _author_read()]
    mock_author_service.find_all_authors.return_value = authors

    response = await client.get("/api/v1/authors_books/")

    assert response.status_code == 200
    assert len(response.json()) == 2
    mock_author_service.find_all_authors.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_by_id_returns_206(client, mock_author_service):
    author = _author_read()
    mock_author_service.find_one_or_none_by_id.return_value = author

    response = await client.get(f"/api/v1/authors_books/{author.id}")

    assert response.status_code == 206
    assert response.json()["id"] == str(author.id)
    mock_author_service.find_one_or_none_by_id.assert_awaited_once_with(author_id=author.id)


@pytest.mark.asyncio
async def test_update_returns_201(client, mock_author_service):
    author = _author_read()
    mock_author_service.update_author_with_books.return_value = author

    response = await client.put(
        f"/api/v1/authors_books/{author.id}",
        json={"name": "Updated Author", "books": [{"title": "Book 2"}]},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Router Author"
    mock_author_service.update_author_with_books.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_returns_204(client, mock_author_service):
    author_id = uuid.uuid4()
    mock_author_service.delete_author.return_value = None

    response = await client.delete(f"/api/v1/authors_books/{author_id}")

    assert response.status_code == 204
    assert response.text == ""
    mock_author_service.delete_author.assert_awaited_once_with(author_id=author_id)


@pytest.mark.asyncio
async def test_find_by_id_not_found_maps_to_404(client, mock_author_service):
    author_id = uuid.uuid4()
    mock_author_service.find_one_or_none_by_id.side_effect = NotFoundError(detail="Author not found")

    response = await client.get(f"/api/v1/authors_books/{author_id}")

    assert response.status_code == 404
    assert response.json()["error_code"] == "Router_not_found"
