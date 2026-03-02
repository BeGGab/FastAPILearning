import uuid
import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.author import SAuthorCreate, SAuthorRead, SAuthorUpdate

from src.repositories.author import AuthorRepository as rep_author

from src.exception.client_exception import ValidationError, NotFoundError

logger = logging.getLogger(__name__)


async def create_author_with_books(
    session: AsyncSession, data: SAuthorCreate
) -> SAuthorRead:
    author, books = await rep_author(session).created(data)
    if not author:
        logger.error(f"Ошибка при создании автора")
        raise ValidationError(detail="Ошибка при создании автора")

    session.add(author)
    await session.flush()
    await session.refresh(author, ["books"])
    return SAuthorRead.model_validate(author, from_attributes=True)


async def find_one_or_none_by_id(session: AsyncSession, id: uuid.UUID) -> SAuthorRead:
    author = await rep_author(session).get_id(id=id)
    if not author:
        logger.error(f"Ошибка при поиске записи в базе данных")
        raise NotFoundError(detail=f"Автор с id {id} не найден")
    return SAuthorRead.model_validate(author, from_attributes=True)


async def find_all_authors(
    session: AsyncSession, skip: int = 0, limit: int = 100, **filter_by
) -> List[SAuthorRead]:
    authors = await rep_author(session).get_all(skip, limit, **filter_by)
    if not authors:
        logger.warning(
            f"Авторы с параметрами {filter_by} не найдены, возвращен пустой список."
        )
        raise NotFoundError(detail=f"Авторы с параметрами {filter_by} не найдены")
    return [SAuthorRead.model_validate(rec, from_attributes=True) for rec in authors]


async def update_author_with_books(
    session: AsyncSession, author_id: uuid.UUID, author_data: SAuthorUpdate
) -> SAuthorRead:
    author = await rep_author(session).update(author_id, author_data)
    if not author:
        logger.error(f"Ошибка при поиске автора")
        raise NotFoundError(author_id=author_id)

    await session.flush()
    await session.refresh(author, ["books"])
    return SAuthorRead.model_validate(author, from_attributes=True)


async def delete_author(session: AsyncSession, author_id: uuid.UUID):
    author = await rep_author(session).get_id(id=author_id)
    if not author:
        logger.error(f"Ошибка при удалении записи из базы данных")
        raise NotFoundError(author_id=author_id)
    await session.delete(author)
