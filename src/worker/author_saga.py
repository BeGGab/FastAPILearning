import logging
from typing import Awaitable, Callable, NoReturn

from sqlalchemy.ext.asyncio import async_sessionmaker
from temporalio.exceptions import ApplicationError

from src.client.bio_author_client import BiographyServiceClient
from src.core.db import async_session_maker
from src.core.enums import SagaStatus
from src.models.saga_request import SagaRequest
from src.repositories.saga_request import SagaRequestRepository
from src.schemas.author import (
    CreateAuthorSagaInput,
    CreateAuthorSagaResult,
    CompensationSummary,
    CompensationResult,
)
from src.worker.author import SAGA_KIND, create_author_step, delete_author_step
from src.worker.biography import create_biography_step, delete_biography_step

logger = logging.getLogger(__name__)


class CreateAuthorSaga:
    def __init__(self, bio_client: BiographyServiceClient, session_factory: async_sessionmaker = async_session_maker):
        self.bio_client = bio_client
        self.session_factory = session_factory

    async def run(self, inp: CreateAuthorSagaInput) -> CreateAuthorSagaResult:
        saga = await self._start(inp.request_id)
        if saga.status == SagaStatus.COMPLETED:
            return CreateAuthorSagaResult(author_id=str(saga.result_id), biography_created=inp.has_biography)
        if saga.status in (SagaStatus.FAILED, SagaStatus.COMPENSATED):
            raise ApplicationError(
                f"Сага {inp.request_id} уже завершилась ошибкой", type="SagaAlreadyFailed", non_retryable=True
            )

        author_id = await create_author_step(self.session_factory, inp)

        if inp.has_biography:
            try:
                await create_biography_step(self.bio_client, author_id, inp)
            except Exception as exc:
                await self._rollback(inp.request_id, author_id, exc)

        await self._finish(inp.request_id, SagaStatus.COMPLETED)
        return CreateAuthorSagaResult(author_id=author_id, biography_created=inp.has_biography)


    async def _rollback(self, request_id: str, author_id: str, exc: Exception) -> NoReturn:
        summary = CompensationSummary(
            biography=await self._compensate(delete_biography_step, self.bio_client, author_id),
            author=await self._compensate(delete_author_step, self.session_factory, author_id),
        )

        status = SagaStatus.COMPENSATED if summary.all_success else SagaStatus.FAILED
        await self._finish(request_id, status, error=f"{type(exc).__name__}: {exc}")
        logger.error("Сага %s откачена (%s): %s", request_id, status.value, summary)
        raise ApplicationError(
            f"Сага {request_id} откачена: {exc}",
            summary.model_dump(),
            type=type(exc).__name__,
            non_retryable=True,
        ) from exc


    @staticmethod
    async def _compensate(step: Callable[..., Awaitable[None]], *args) -> CompensationResult:
        try:
            await step(*args)
            return CompensationResult(attempted=True, success=True)
        except Exception as exc:
            logger.exception("Компенсация %s не удалась", step.__name__)
            return CompensationResult(attempted=True, success=False, details=str(exc))

    async def _start(self, request_id: str) -> SagaRequest:
        async with self.session_factory() as session:
            saga = await SagaRequestRepository(session).start(SAGA_KIND, request_id)
            await session.commit()
            return saga

    async def _finish(self, request_id: str, status: SagaStatus, error: str | None = None) -> None:
        async with self.session_factory() as session:
            await SagaRequestRepository(session).finish(SAGA_KIND, request_id, status, error)
            await session.commit()