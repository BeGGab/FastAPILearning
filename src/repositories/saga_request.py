from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert 
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import SagaStatus
from src.models.saga_request import SAGA_UNIQUE, SagaRequest


class SagaRequestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    
    @staticmethod
    def _key(kind: str, request_id: str) -> tuple:
        return SagaRequest.kind == kind, SagaRequest.request_id == request_id

    async def get(self, kind: str, request_id: str, *, for_update: bool = False) -> SagaRequest | None:
        query = (
            select(SagaRequest)
            .where(*self._key(kind, request_id))
            .execution_options(populate_existing=True)
        )
        if for_update:
            query = query.with_for_update()
        return (await self.session.execute(query)).scalar_one_or_none()


    async def start(self, kind: str, request_id: str) -> SagaRequest:
        await self.session.execute(
            insert(SagaRequest)
            .values(kind=kind, request_id=request_id, status=SagaStatus.PENDING)
            .on_conflict_do_nothing(constraint=SAGA_UNIQUE)
        )
        await self.session.execute(
            update(SagaRequest)
            .where(*self._key(kind, request_id),
            SagaRequest.status.in_([SagaStatus.PENDING, SagaStatus.PROCESSING])
            )
            .values(status=SagaStatus.PROCESSING, attempts=SagaRequest.attempts + 1)
        )
        return await self.get(kind, request_id)

    async def finish(self, kind: str, request_id: str, status: SagaStatus, error: str | None = None) -> None:
        await self.session.execute(
            update(SagaRequest)
            .where(*self._key(kind, request_id))
            .values(status=status, error=error[:2000] if error else None)
        )
        
