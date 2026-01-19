import uuid
import logging
from typing import List
from sqlalchemy import select, update, delete, event, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.author_schemas import SAuthorCreate, SAuthorRead, SAuthorUpdate
from src.models.author_models import Author, Book
from src.exception.base import NotFoundError
from src.dao.base import BaseDAO


logger = logging.getLogger(__name__)


async def create_author_with_books(
    session: AsyncSession, data: SAuthorCreate
) -> Author:
    try:
        author, books = data.to_orm_models()
        session.add(author)
        
        if books:
            session.add_all(books)
            logger.info(f"Автор {author.name} создан с {len(books)} книгами")
        else:
            logger.info(f"Автор {author.name} создан без книг")

        await session.flush()
        await session.refresh(author, ["books"])
        return author
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении записи в базу данных: {e}")
        raise


async def find_one_or_none_by_id(session: AsyncSession, id: uuid.UUID) -> Author:
    try:
        query = select(Author).options(joinedload(Author.books)).filter_by(id=id)
        result = await session.execute(query)
        record = result.scalar()
        if not record:
            raise NotFoundError(f"Автор с id {id} не найден")
        logger.info(f"Запись {record.name} успешно найдена в базе данных")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при поиске записи в базе данных: {e}")
        raise


async def find_all_authors(session: AsyncSession, **filter_by) -> list[SAuthorRead]:
    try:
        query = (
            select(Author).options(selectinload(Author.books)).filter_by(**filter_by)
        )
        result = await session.execute(query)
        record = result.scalars().all()
        logger.info(f"Записи {len(record)} успешно найдены в базе данных")
        return list(record)
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при поиске записей в базе данных: {e}")
        raise


async def update_author_with_books(
    session: AsyncSession, author_id: uuid.UUID, author_data: SAuthorUpdate
) -> Author:
    author = await find_one_or_none_by_id(session=session, id=author_id)

    try:
        await author_data.apply_updates(author, session)

        logger.info(f"Запись {author.name} успешно обновлена в базе данных")
        await session.flush()
        await session.refresh(author, ["books"])
        return author
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при обновлении записи в базе данных: {e}")
        raise


async def delete_author(session: AsyncSession, author_id: uuid.UUID):
    author = await find_one_or_none_by_id(session, id=author_id)
    try:
        await session.delete(author)
        logger.info(f"Запись {author.name} успешно удалена из базы данных")
        return author
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при удалении записи из базы данных: {e}")
        raise
