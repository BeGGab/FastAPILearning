import uuid
import logger
from typing import List
from sqlalchemy import select, update, delete, event, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.author_schemas import SAuthorCreate, SAuthorRead
from src.models.author_models import Author, Book
from src.dao.base import BaseDAO


async def create_author_with_books(
    session: AsyncSession, data: SAuthorCreate
) -> Author:
    try:
        author_dict = data.model_dump()
        books_data = author_dict.pop("books", [])

        author = Author(**author_dict)
        author.books = [Book(**book_data) for book_data in books_data]

        session.add(author)
        logger.logger.info(f"Запись {author.name} успешно добавлена в базу данных")
        await session.flush()
        await session.refresh(author, ["books"])
        return author
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при добавлении записи в базу данных: {e}")
        raise


async def find_one_or_none_by_id(session: AsyncSession, id: uuid.UUID) -> Author:
    try:
        query = select(Author).options(joinedload(Author.books)).filter_by(id=id)
        result = await session.execute(query)
        record = result.scalar()
        logger.logger.info(f"Запись {record.name} успешно найдена в базе данных")
        return record
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при поиске записи в базе данных: {e}")
        raise


async def find_all_authors(session: AsyncSession, **filter_by) -> list[SAuthorRead]:
    try:
        query = (
            select(Author).options(selectinload(Author.books)).filter_by(**filter_by)
        )
        result = await session.execute(query)
        record = result.scalars().all()
        logger.logger.info(f"Записи {len(record)} успешно найдены в базе данных")
        return list(record)
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при поиске записей в базе данных: {e}")
        raise


async def update_author_with_books(
    session: AsyncSession, author_id: uuid.UUID, author_data: SAuthorCreate
) -> Author:
    author = await find_one_or_none_by_id(session=session, id=author_id)
    logger.logger.info(f"Запись {author.name} успешно найдена в базе данных")
    if not author:
        raise ValueError(f"Автор с id {author_id} не найден")

    try:
        author_dict = author_data.model_dump()
        books_data = author_dict.pop("books", [])

        author.name = author_dict["name"]
        author.books = [Book(**book_data) for book_data in books_data]
        logger.logger.info(f"Запись {author.name} успешно обновлена в базе данных")
        await session.refresh(author, attribute_names=["books"])
        return author
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при обновлении записи в базе данных: {e}")
        raise


async def delete_author(session: AsyncSession, author_id: uuid.UUID):
    author = await find_one_or_none_by_id(session, id=author_id)
    logger.logger.info(f"Запись {author.name} успешно найдена в базе данных")
    if not author:
        raise ValueError(f"Автор с id {author_id} не найден")
    try:
        await session.delete(author)
        logger.logger.info(f"Запись {author.name} успешно удалена из базы данных")
        return author
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при удалении записи из базы данных: {e}")
        raise
