import uuid
import logging

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from temporalio.client import WorkflowFailureError

from src.core.redis import RedisClient

from src.client.bio_author_client import BiographyServiceClient
from src.schemas.author import SAuthorCreate, SAuthorRead, SAuthorUpdate
from src.schemas.author import CreateAuthorSagaInput

from src.repositories.author import AuthorRepository
from src.schemas.book import SagaBookInput
from src.exception.client_exception import NotFoundError
from src.exception.server_exception import InternalServerError
from src.exception.biography_exception import BiographyNotFoundError
from src.worker.saga_starter import AuthorSagaStarter

logger = logging.getLogger(__name__)



class AuthorService:
    def __init__(
    self, 
    session: AsyncSession, 
    repository: AuthorRepository, 
    cache: RedisClient,
    author_client: BiographyServiceClient,
    saga_starter: AuthorSagaStarter):
        self.session = session
        self.cache = cache
        self.repository = repository
        self.author_client = author_client
        self.saga_starter = saga_starter


    async def create_author_with_books(
        self,
        author_data: SAuthorCreate,
        *,
        request_id: str | None = None,
    ) -> SAuthorRead:

        rid = request_id or str(uuid.uuid4())
        saga_input = CreateAuthorSagaInput(
            request_id=rid,
            name=author_data.name,
            books=[SagaBookInput(title=b.title) for b in author_data.books],
            biography_text=author_data.biography_text,
            year_of_birth=author_data.year_of_birth,
            year_of_death=author_data.year_of_death,
        )
        try:
            result = await self.saga_starter.create_author(saga_input)
        except WorkflowFailureError as exc:
            logger.error("Сага создания автора %s упала: %s", rid, exc.cause)
            raise InternalServerError(
                detail="Не удалось создать автора через сагу",
                request_id=rid,
            ) from exc

        if not result.author_id:
            raise InternalServerError(detail="Сага завершилась без author_id")

        return await self.find_one_or_none_by_id(uuid.UUID(result.author_id))


    async def find_one_or_none_by_id(
        self,
        author_id: uuid.UUID) -> SAuthorRead:
        cache_key = f"author:{author_id}"
        cached = await self.cache.get(cache_key)
        if not cached:
            author = await self.repository.get_id(id=author_id)
            if not author:
                logger.error("Ошибка при поиске записи в базе данных")
                raise NotFoundError(detail=f"Автор с id {author_id} не найден")
            author_data = SAuthorRead.model_validate(author, from_attributes=True)
            try:
                bio = await self.author_client.get_biography(author_id)
            except BiographyNotFoundError:
                bio = None
            author_data = author_data.to_bio_response(bio)
            await self.cache.set(cache_key, author_data.model_dump())
            return SAuthorRead.model_validate(author_data)

        return SAuthorRead.model_validate(cached)


    async def find_all_authors(
        self, skip: int = 0, limit: int = 100, **filter_by
    ) -> List[SAuthorRead]:
        cache_key = f"authors:{filter_by, skip, limit}"
        cached_authors = await self.cache.get(cache_key)
        if cached_authors:
            return SAuthorRead.from_cache_many(cached_authors)
            
        authors = await self.repository.get_all(skip, limit, **filter_by)
        if not authors:
            logger.warning(f"Авторы с параметрами {filter_by} не найдены, возвращен пустой список.")
            raise NotFoundError(detail=f"Авторы с параметрами {filter_by} не найдены")
        authors_read = SAuthorRead.from_orm_many(authors)
        await self.cache.set(cache_key, SAuthorRead.to_cache_many(authors_read))
        return authors_read


    async def update_author_with_books(
        self,
        author_id: uuid.UUID,
        author_data: SAuthorUpdate,
    ) -> SAuthorRead:
        author = await self.repository.update(author_id, author_data)
        if not author:
            logger.error("Ошибка при поиске автора")
            raise NotFoundError(detail=f"Автор с id {author_id} не найден")

        await self.session.flush()
        await self.session.refresh(author, ["books"])

        cache_key = f"author:{author_id}"
        await self.cache.set(cache_key, SAuthorRead.model_validate(author, from_attributes=True).model_dump())

        return SAuthorRead.model_validate(author, from_attributes=True)


    async def delete_author(self, author_id: uuid.UUID):
        author = await self.repository.get_id(id=author_id)
        if not author:
            logger.error("Ошибка при удалении записи из базы данных")
            raise NotFoundError(detail=f"Автор с id {author_id} не найден")


        await self.cache.delete(f"author:{author_id}")
        await self.session.delete(author)

        
