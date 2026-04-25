import uuid
import logging
import ujson

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.redis import RedisClient

from src.client.bio_author_client import AuthorServiceClient
from src.schemas.author import SAuthorCreate, SAuthorRead, SAuthorUpdate

from src.repositories.author import AuthorRepository

from src.exception.client_exception import ValidationError, NotFoundError
from src.exception.server_exception import InternalServerError


logger = logging.getLogger(__name__)



class AuthorService:
    def __init__(
    self, 
    session: AsyncSession, 
    repository: AuthorRepository, 
    cache: RedisClient,
    author_client: AuthorServiceClient):
        self.session = session
        self.cache = cache
        self.repository = repository
        self.author_client = author_client


    async def create_author_with_books(
        self, author_data: SAuthorCreate) -> SAuthorRead:
        
        author, _books = await self.repository.created(author_data=author_data)
        if not author:
            logger.error(f"Ошибка при создании автора")
            raise InternalServerError(detail="Ошибка при создании автора")

        self.session.add(author)
        await self.session.flush()
        await self.session.refresh(author, ["books"])

        author_read_data = SAuthorRead.model_validate(author, from_attributes=True)
       
            
        bio_data = await self.author_client.create_to_author(author_id=author.id, author_data=author_data)
        if bio_data is None:
            logger.warning(f"Биография для автора {author.id} не создана (пустой ответ или ошибка микросервиса).")
            raise InternalServerError(detail=f"Биография для автора {author.id} не создана")
        author_read_data = self.repository.apply_biography_to_author_data(
            author_read_data, bio_data
        )
        
        cache_key = f"author:{author.id}"
        await self.cache.set(cache_key, author_read_data.model_dump_json())
        
        return author_read_data


    async def find_one_or_none_by_id(
        self,
        author_id: uuid.UUID) -> SAuthorRead:
        cache_key = f"author:{author_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            author_data = SAuthorRead.model_validate_json(cached)
            bio_data = await self.author_client.get_author(author_id=author_id)
            enriched_author = self.repository.apply_biography_to_author_data(author_data, bio_data)
            if enriched_author.model_dump() != author_data.model_dump():
                await self.cache.set(cache_key, enriched_author.model_dump_json())
            return enriched_author

        author = await self.repository.get_id(id=author_id)
        if not author:
            logger.error(f"Ошибка при поиске записи в базе данных")
            raise NotFoundError(detail=f"Автор с id {author_id} не найден")

        author_data = SAuthorRead.model_validate(author, from_attributes=True)

        bio_data = await self.author_client.get_author(author_id=author_id)
        author_data = self.repository.apply_biography_to_author_data(author_data, bio_data)
        await self.cache.set(cache_key, author_data.model_dump_json())

        return author_data


    async def find_all_authors(
        self, skip: int = 0, limit: int = 100, **filter_by
    ) -> List[SAuthorRead]:
        cache_key = f"authors:{filter_by, skip, limit}"
        cached_authors = await self.cache.get(cache_key)
        if cached_authors:
            return [
                SAuthorRead.model_validate_json(author_json)
                for author_json in ujson.loads(cached_authors)
            ]

        authors = await self.repository.get_all(skip, limit, **filter_by)
        if not authors:
            logger.warning(f"Авторы с параметрами {filter_by} не найдены, возвращен пустой список.")
            raise NotFoundError(detail=f"Авторы с параметрами {filter_by} не найдены")

        authors_json = ujson.dumps([SAuthorRead.model_validate(rec, from_attributes=True).model_dump_json() for rec in authors])
        await self.cache.set(cache_key, authors_json)
        return [SAuthorRead.model_validate(rec, from_attributes=True) for rec in authors]


    async def update_author_with_books(
        self,
        author_id: uuid.UUID,
        author_data: SAuthorUpdate,
    ) -> SAuthorRead:
        author = await self.repository.update(author_id, author_data)
        if not author:
            logger.error(f"Ошибка при поиске автора")
            raise NotFoundError(detail=f"Автор с id {author_id} не найден")

        await self.session.flush()
        await self.session.refresh(author, ["books"])

        cache_key = f"author:{author_id}"
        await self.cache.set(cache_key, SAuthorRead.model_validate(author, from_attributes=True).model_dump_json())

        return SAuthorRead.model_validate(author, from_attributes=True)


    async def delete_author(self, author_id: uuid.UUID):
        author = await self.repository.get_id(id=author_id)
        if not author:
            logger.error(f"Ошибка при удалении записи из базы данных")
            raise NotFoundError(detail=f"Автор с id {author_id} не найден")


        await self.cache.delete(f"author:{author_id}")
        await self.session.delete(author)

        
