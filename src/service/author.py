import uuid
import logging
import json
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from redress import CircuitOpenError

from src.core.redis import RedisDep

from src.client.bio_author_client import AuthorClientDep
from src.schemas.author import SAuthorCreate, SAuthorRead, SAuthorUpdate

from src.repositories.author import AuthorRepository as rep_author

from src.exception.client_exception import ValidationError, NotFoundError

logger = logging.getLogger(__name__)


async def create_author_with_books(
    session: AsyncSession,
    author_data: SAuthorCreate,
    redis: RedisDep,
    author_client: AuthorClientDep,
) -> SAuthorRead:
    author, books = await rep_author(session).created(author_data=author_data)
    if not author:
        logger.error(f"Ошибка при создании автора")
        raise ValidationError(detail="Ошибка при создании автора")

    session.add(author)
    await session.flush()
    await session.refresh(author, ["books"])

    author_read_data = SAuthorRead.model_validate(author, from_attributes=True)
    try:
        if (
            author_data.biography_text is not None
            and author_data.year_of_birth is not None
            and author_data.year_of_death is not None
        ):
            # HTTP к src_external открывает новую транзакцию; микросервис проверяет автора
            # запросом к главному API — строка должна быть уже закоммичена.
            await session.commit()
            bio_data = await author_client.create_to_author(
                author_id=author.id,
                author_data=author_data,
            )
            author_read_data = rep_author(session).apply_biography_to_author_data(
                author_read_data, bio_data
            )
    except CircuitOpenError:
        logger.warning(
            f"Circuit Breaker для сервиса биографий открыт. Запрос для автора {author.id} не выполнен."
        )

    cache_key = f"author:{author.id}"
    try:
        await redis.delete(cache_key)
        await redis.setex(
            cache_key,
            3600,
            author_read_data.model_dump_json(),
        )
    except Exception as e:
        logger.warning(
            f"Не удалось обновить кэш после создания автора {author.id}: {e}"
        )

    return author_read_data


async def find_one_or_none_by_id(
    session: AsyncSession,
    author_id: uuid.UUID,
    redis: RedisDep,
    author_client: AuthorClientDep,
) -> SAuthorRead:
    author_repo = rep_author(session)
    cache_key = f"author:{author_id}"
    cached = await redis.get(cache_key)
    if cached:
        author_data = SAuthorRead.model_validate_json(cached)
        try:
            bio_data = await author_client.get_author(author_id=author_id)
            enriched_author = author_repo.apply_biography_to_author_data(
                author_data, bio_data
            )

            if enriched_author.model_dump() != author_data.model_dump():
                await redis.setex(cache_key, 3600, enriched_author.model_dump_json())

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

    author = await author_repo.get_id(id=author_id)
    if not author:
        logger.error(f"Ошибка при поиске записи в базе данных")
        raise NotFoundError(detail=f"Автор с id {author_id} не найден")

    author_data = SAuthorRead.model_validate(author, from_attributes=True)
    try:
        bio_data = await author_client.get_author(author_id=author_id)
        author_data = author_repo.apply_biography_to_author_data(author_data, bio_data)
    except CircuitOpenError:
        logger.warning(
            f"Circuit Breaker для сервиса биографий открыт. Запрос для автора {author_id} не выполнен."
        )
    except Exception as e:
        logger.warning(f"Не удалось обогатить автора {author_id} биографией: {e}")

    try:
        await redis.setex(cache_key, 3600, author_data.model_dump_json())
    except Exception as e:
        logger.warning(f"Не удалось записать автора {author_id} в кэш: {e}")

    return author_data


async def find_all_authors(
    session: AsyncSession, redis: RedisDep, skip: int = 0, limit: int = 100, **filter_by
) -> List[SAuthorRead]:
    cache_key = f"authors:{filter_by, skip, limit}"
    cached_authors = await redis.get(cache_key)
    if cached_authors:
        return [
            SAuthorRead.model_validate_json(author_json)
            for author_json in json.loads(cached_authors)
        ]

    authors = await rep_author(session).get_all(skip, limit, **filter_by)
    if not authors:
        logger.warning(
            f"Авторы с параметрами {filter_by} не найдены, возвращен пустой список."
        )
        raise NotFoundError(detail=f"Авторы с параметрами {filter_by} не найдены")
    try:
        authors_json = json.dumps(
            [
                SAuthorRead.model_validate(rec, from_attributes=True).model_dump_json()
                for rec in authors
            ]
        )
        await redis.setex(cache_key, 3600, authors_json)
    except Exception as e:
        logger.warning(f"Не удалось записать авторов в кэш: {e}")
    return [SAuthorRead.model_validate(rec, from_attributes=True) for rec in authors]


async def update_author_with_books(
    session: AsyncSession,
    author_id: uuid.UUID,
    author_data: SAuthorUpdate,
    redis: RedisDep,
) -> SAuthorRead:
    author = await rep_author(session).update(author_id, author_data)
    if not author:
        logger.error(f"Ошибка при поиске автора")
        raise NotFoundError(detail=f"Автор с id {author_id} не найден")

    await session.flush()
    await session.refresh(author, ["books"])

    cache_key = f"author:{author_id}"
    try:
        await redis.delete(cache_key)
        await redis.setex(
            cache_key,
            3600,
            SAuthorRead.model_validate(author, from_attributes=True).model_dump_json(),
        )
    except Exception as e:
        logger.warning(
            f"Не удалось обновить кэш после изменения автора {author_id}: {e}"
        )

    return SAuthorRead.model_validate(author, from_attributes=True)


async def delete_author(session: AsyncSession, author_id: uuid.UUID, redis: RedisDep):
    author = await rep_author(session).get_id(id=author_id)
    if not author:
        logger.error(f"Ошибка при удалении записи из базы данных")
        raise NotFoundError(detail=f"Автор с id {author_id} не найден")

    await session.delete(author)

    try:
        await redis.delete(f"author:{author_id}")
    except Exception as e:
        logger.warning(f"Не удалось удалить ключ кэша автора {author_id}: {e}")
