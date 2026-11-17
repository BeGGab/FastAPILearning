import uuid
from unittest.mock import AsyncMock

import pytest
from temporalio.exceptions import ApplicationError

from src.core.enums import SagaStatus
from src.exception.biography_exception import BiographyServiceUnavailableError
from src.repositories.author import AuthorRepository
from src.repositories.saga_request import SagaRequestRepository
from src.schemas.author import CreateAuthorSagaInput
from src.worker.author import SAGA_KIND
from src.worker.author_saga import CreateAuthorSaga


def make_input() -> CreateAuthorSagaInput:
    return CreateAuthorSagaInput(
        request_id=str(uuid.uuid4()),
        name="Лев Толстой",
        books=[],
        biography_text="Русский писатель",
        year_of_birth=1828,
        year_of_death=1910,
    )


async def test_saga_run_twice_creates_one_author(async_session_factory):
    bio_client = AsyncMock()
    saga = CreateAuthorSaga(bio_client, async_session_factory)
    inp = make_input()

    first = await saga.run(inp)
    second = await saga.run(inp)  # как будто Temporal повторил activity

    assert first.author_id == second.author_id
    bio_client.create_biography_for_author.assert_awaited_once()


async def test_saga_compensates_when_biography_fails(async_session_factory):
    bio_client = AsyncMock()
    bio_client.create_biography_for_author.side_effect = BiographyServiceUnavailableError("503")
    saga = CreateAuthorSaga(bio_client, async_session_factory)
    inp = make_input()

    with pytest.raises(ApplicationError) as error:
        await saga.run(inp)

    assert error.value.non_retryable
    bio_client.delete_biography.assert_awaited_once()
    async with async_session_factory() as session:
        row = await SagaRequestRepository(session).get(SAGA_KIND, inp.request_id)
        assert row.status == SagaStatus.COMPENSATED
        assert await AuthorRepository(session).get_id(id=row.result_id) is None