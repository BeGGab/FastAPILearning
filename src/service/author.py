import uuid
import logging
import ujson
import redress 
from typing import List, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.redis import RedisDep

from redress import CircuitOpenError
from src.client.bio_author_client import AuthorClientDep
from src.schemas.author import SAuthorCreate, SAuthorRead, SAuthorUpdate

from src.repositories.author import AuthorRepository as rep_author

from src.exception.client_exception import ValidationError, NotFoundError

from src.core.config import Settings

logger = logging.getLogger(__name__)

settings = Settings()


class AuthorService:
    def __init__(self, session: AsyncSession, redis: RedisDep):
        self.session = session
        self.redis = redis

    @redress.retry(max_attempts=3, deadline_s=10, strategy=redress.strategies.decorrelated_jitter(max_s=5.0))
    async def set_cache(self, key: str, value: Any, ttl: int):
        await self.redis.setex(key, ttl, value)

    async def create_author_with_books(
        self, author_data: SAuthorCreate,
        author_client: AuthorClientDep
    ) -> SAuthorRead:
        author, books = await rep_author(self.session).created(author_data=author_data)
        if not author:
            logger.error(f"Ошибка при создании автора")
            raise ValidationError(detail="Ошибка при создании автора")

        self.session.add(author)
        await self.session.flush()
        await self.session.refresh(author, ["books"])

        author_read_data = SAuthorRead.model_validate(author, from_attributes=True)
        if (
            author_data.biography_text is not None
            and author_data.year_of_birth is not None
            and author_data.year_of_death is not None
        ):
            await self.session.commit()
            try:
                bio_data = await author_client.create_to_author(
                    author_id=author.id, author_data=author_data
                )
                if bio_data is None:
                    logger.warning(
                        "Биография для автора %s не создана (пустой ответ или ошибка микросервиса).",
                        author.id,
                    )
                author_read_data = rep_author(self.session).apply_biography_to_author_data(
                    author_read_data, bio_data
                )
            except CircuitOpenError:
                logger.warning(
                    "Circuit Breaker биографий: биография для автора %s не создана.",
                    author.id,
                )

        cache_key = f"author:{author.id}"
        await self.set_cache(cache_key, author_read_data.model_dump_json(), settings.ttl)

        return author_read_data


    async def find_one_or_none_by_id(
        self,
        author_id: uuid.UUID,
        author_client: AuthorClientDep,
    ) -> SAuthorRead:
        cache_key = f"author:{author_id}"
        cached = await self.redis.get(cache_key)
        if cached:
            author_data = SAuthorRead.model_validate_json(cached)
            try:
                bio_data = await author_client.get_author(author_id=author_id)
                enriched_author = rep_author(self.session).apply_biography_to_author_data(
                    author_data, bio_data
                )

                if enriched_author.model_dump() != author_data.model_dump():
                    await self.set_cache(cache_key, enriched_author.model_dump_json(), settings.ttl)

                return enriched_author
            except CircuitOpenError:
                logger.warning(
                    f"Circuit Breaker для сервиса биографий открыт. Запрос для автора {author_id} не выполнен."
                )
                return author_data
            except Exception as e:
                logger.warning(
                    f"Не удалось дообогатить автора {author_id} из сервиса биографий: {e}"
                )
                return author_data

        author = await rep_author(self.session).get_id(id=author_id)
        if not author:
            logger.error(f"Ошибка при поиске записи в базе данных")
            raise NotFoundError(detail=f"Автор с id {author_id} не найден")

        author_data = SAuthorRead.model_validate(author, from_attributes=True)
        try:
            bio_data = await author_client.get_author(author_id=author_id)
            author_data = rep_author(self.session).apply_biography_to_author_data(author_data, bio_data)
        except CircuitOpenError:
            logger.warning(
                f"Circuit Breaker для сервиса биографий открыт. Запрос для автора {author_id} не выполнен."
            )
        except Exception as e:
            logger.warning(f"Не удалось обогатить автора {author_id} биографией: {e}")

        try:
            await self.set_cache(cache_key, author_data.model_dump_json(), settings.ttl)
        except Exception as e:
            logger.warning(f"Не удалось записать автора {author_id} в кэш: {e}")

        return author_data


    async def find_all_authors(
        self, skip: int = 0, limit: int = 100, **filter_by
    ) -> List[SAuthorRead]:
        cache_key = f"authors:{filter_by, skip, limit}"
        cached_authors = await self.redis.get(cache_key)
        if cached_authors:
            return [
                SAuthorRead.model_validate_json(author_json)
                for author_json in ujson.loads(cached_authors)
            ]

        authors = await rep_author(self.session).get_all(skip, limit, **filter_by)
        if not authors:
            logger.warning(
                f"Авторы с параметрами {filter_by} не найдены, возвращен пустой список."
            )
            raise NotFoundError(detail=f"Авторы с параметрами {filter_by} не найдены")
        try:
            authors_json = ujson.dumps(
                [
                    SAuthorRead.model_validate(rec, from_attributes=True).model_dump_json()
                    for rec in authors
                ]
            )
            await self.set_cache(cache_key, authors_json, settings.ttl)
        except Exception as e:
            logger.warning(f"Не удалось записать авторов в кэш: {e}")
        return [SAuthorRead.model_validate(rec, from_attributes=True) for rec in authors]


    async def update_author_with_books(
        self,
        author_id: uuid.UUID,
        author_data: SAuthorUpdate,
    ) -> SAuthorRead:
        author = await rep_author(self.session).update(author_id, author_data)
        if not author:
            logger.error(f"Ошибка при поиске автора")
            raise NotFoundError(detail=f"Автор с id {author_id} не найден")

        await self.session.flush()
        await self.session.refresh(author, ["books"])

        cache_key = f"author:{author_id}"
        await self.set_cache(cache_key, SAuthorRead.model_validate(author, from_attributes=True).model_dump_json(), settings.ttl)

        return SAuthorRead.model_validate(author, from_attributes=True)


    async def delete_author(self, author_id: uuid.UUID):
        author = await rep_author(self.session).get_id(id=author_id)
        if not author:
            logger.error(f"Ошибка при удалении записи из базы данных")
            raise NotFoundError(detail=f"Автор с id {author_id} не найден")

        await self.session.delete(author)

        await self.redis.delete(f"author:{author_id}")
