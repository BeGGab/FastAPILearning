import uuid
import logging
from typing import List
from sqlalchemy import select, update, delete, event, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.author_schemas import SAuthorCreate, SAuthorRead, SAuthorUpdate
from src.models.author_models import Author
from src.exception.client_exception import BadRequestError
from src.exception.business import AuthorNotFoundError

logger = logging.getLogger(__name__)


async def get_author_by_id(session: AsyncSession, author_id: uuid.UUID) -> Author:
    query = select(Author).options(joinedload(Author.books)).filter_by(id=author_id)
    result = await session.execute(query)
    author = result.scalar()
    if not author:
        logger.error(f"Ошибка при поиске записи в базе данных")
        raise AuthorNotFoundError(author_id=author_id)
    return author


async def create_author_with_books(
    session: AsyncSession, data: SAuthorCreate
) -> SAuthorRead:
    try:
        author, books = data.to_orm_models()
        session.add(author)

        await session.flush()
        await session.refresh(author, ["books"])
        return SAuthorRead.model_validate(author, from_attributes=True)
    except IntegrityError as e:
        raise BadRequestError(detail=str(e))


async def find_one_or_none_by_id(session: AsyncSession, id: uuid.UUID) -> SAuthorRead:
    query = select(Author).options(joinedload(Author.books)).filter_by(id=id)
    result = await session.execute(query)
    record = result.scalar()
    if not record:
        raise AuthorNotFoundError(author_id=id)
    return SAuthorRead.model_validate(record, from_attributes=True)


async def find_all_authors(session: AsyncSession, **filter_by) -> List[SAuthorRead]:
    query = select(Author).options(selectinload(Author.books)).filter_by(**filter_by)
    result = await session.execute(query)
    record = result.scalars().all()
    if not record:
        raise AuthorNotFoundError(detail=f"Авторы с параметрами {filter_by} не найдены")
    return [SAuthorRead.model_validate(rec, from_attributes=True) for rec in record]


async def update_author_with_books(
    session: AsyncSession, author_id: uuid.UUID, author_data: SAuthorUpdate
) -> SAuthorRead:
    author = await get_author_by_id(session=session, author_id=author_id)
    if not author:
        logger.error(f"Ошибка при поиске автора")
        raise AuthorNotFoundError(author_id=author_id)
    try:
        await author_data.apply_updates(author)

        await session.flush()
        await session.refresh(author, ["books"])
        return SAuthorRead.model_validate(author, from_attributes=True)
    except IntegrityError as e:
        raise BadRequestError(detail=str(e))


async def delete_author(session: AsyncSession, author_id: uuid.UUID):
    author = await get_author_by_id(session, author_id=author_id)
    if not author:
        logger.error(f"Ошибка при удалении записи из базы данных")
        raise AuthorNotFoundError(author_id=author_id)
    await session.delete(author)
