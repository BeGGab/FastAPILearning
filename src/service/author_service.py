import uuid
from typing import List
from sqlalchemy import select, update, delete, event, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.author_schemas import SAuthorCreate, SAuthorRead
from src.models.author_models import Author, Book
from src.dao.base import BaseDAO


class AuthorDAO(BaseDAO):
    model = Author


    @classmethod
    async def create_author_with_books(
        cls, session: AsyncSession, author_data: SAuthorCreate
    ) -> Author:
        books_data = author_data.prepare_author_db_data()
        author = Author(**books_data)

        session.add(author)
        await session.flush()
        await session.refresh(author, ["books"])
        return author

    @classmethod
    async def find_one_or_none_by_id(
        cls, session: AsyncSession, id: uuid.UUID
    ) -> Author:
        query = select(cls.model).options(joinedload(cls.model.books)).filter_by(id=id)
        result = await session.execute(query)
        return result.scalar()

    @classmethod
    async def find_all_authors(
        cls, session: AsyncSession, **filter_by
    ) -> list[SAuthorRead]:
        query = (
            select(cls.model)
            .options(selectinload(cls.model.books))
            .filter_by(**filter_by)
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def update_author_with_books(
        cls, session: AsyncSession, author_id: uuid.UUID, author_data: SAuthorCreate
    ) -> Author:
        author = await cls.find_one_or_none_by_id(session=session, id=author_id)
        if not author:
            raise ValueError(f"Автор с id {author_id} не найден")

        books_data = author_data.prepare_author_db_data()
        author.name = books_data["name"]
        author.books = books_data["books"]

        session.add(author)
        await session.flush()
        await session.refresh(author, attribute_names=["books"])
        return author
