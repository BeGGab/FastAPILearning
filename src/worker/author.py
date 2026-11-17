import uuid

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.repositories.author import AuthorRepository
from src.repositories.saga_request import SagaRequestRepository
from src.schemas.author import CreateAuthorSagaInput

SAGA_KIND ="create_author"

async def create_author_step(session_factory: async_sessionmaker, inp: CreateAuthorSagaInput) -> str:
    async with session_factory() as session:
        saga = await SagaRequestRepository(session).get(SAGA_KIND, inp.request_id, for_update=True)
        if saga is None:
            raise RuntimeError(f"Сага {inp.request_id} не стартовала")
        if saga.result_id is not None:
            return str(saga.result_id)
        
        author, _ = await AuthorRepository(session).created(author_data=inp.to_author_create())
        saga.result_id = author.id
        await session.commit()
        return str(author.id)


async def delete_author_step(session_factory: async_sessionmaker, author_id: str) -> None:
    async with session_factory() as session:
        repository = AuthorRepository(session)
        author = await repository.get_id(id=uuid.UUID(author_id))
        if author is None:
            return
        await session.delete(author)
        await session.commit()
        