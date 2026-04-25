import pytest
import pytest_asyncio
import redis.asyncio as redis
import os

from httpx import AsyncClient, ASGITransport
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from unittest.mock import AsyncMock

from src.application import get_app
from src.core.db import Base
from src.core.redis import RedisClient
from src.repositories.author import AuthorRepository
from src.core.dependencies import get_author_service
from src.service.author import AuthorService

os.environ.setdefault("TESTCONTAINERS_RYUK_DISABLED", "true")


@pytest.fixture(scope="session", autouse=True)
def redis_container():
    with RedisContainer("redis:7-alpine") as redis:
        yield redis


@pytest_asyncio.fixture
async def redis_client(redis_container):
    client = redis.from_url(
        redis_container.get_connection_url(),
        encoding="utf-8",
        decode_responses=True
    )

    yield client 

    await client.flushdb()
    await client.aclose()


@pytest_asyncio.fixture
async def cache_service(redis_client) -> RedisClient:
    return RedisClient(redis_client)



@pytest.fixture(scope="session", autouse=True)
def postgres_container():
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres


@pytest_asyncio.fixture(scope="session")
async def async_engine(postgres_container):
    database_url = postgres_container.get_connection_url()
    database_url = (
        database_url
        .replace("postgresql+psycopg2://", "postgresql+asyncpg://")
        .replace("postgresql://", "postgresql+asyncpg://")
        .replace("postgres://", "postgresql+asyncpg://")
    )
    engine = create_async_engine(database_url, echo=False)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture(scope="session")
async def async_session_factory(async_engine):
    return async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(async_session_factory, setup_database):
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture
async def author_repository(db_session):
    return AuthorRepository(db_session)


@pytest.fixture
def mock_author_client():
    client = AsyncMock()
    client.create_to_author = AsyncMock(
        return_value={
            "text": "Test biography",
            "year_of_birth": 1900,
            "year_of_death": 1950,
        }
    )
    client.get_author = AsyncMock(return_value=None)
    return client


@pytest_asyncio.fixture
async def author_service(db_session, author_repository, cache_service, mock_author_client):
    return AuthorService(
        session=db_session,
        repository=author_repository,
        cache=cache_service,
        author_client=mock_author_client,
    )


@pytest.fixture
def app():
    return get_app()


@pytest_asyncio.fixture
async def async_client(app, author_service):
    app.dependency_overrides[get_author_service] = lambda: author_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()