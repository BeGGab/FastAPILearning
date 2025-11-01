from sqlalchemy import select, update, delete, event, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from src.dao.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from src.author.models import Author, Book






class AuthorDAO(BaseDAO):
    model = Author
    
    @classmethod
    async def create_author_with_books(cls, session: AsyncSession, author_data: dict) -> Author:
        books_data = author_data.pop("books")
        author = Author(**author_data, books=[Book(**book) for book in books_data])
        session.add(author)
        await session.commit()
        await session.refresh(author, ["books"])
        return author
    
    @classmethod
    async def find_one_or_none_by_id(cls, session: AsyncSession, **filter_by) -> Author | None:
        query = (
            select(cls.model)
            .options(joinedload(cls.model.books))
            .filter_by(**filter_by)
        )
        result = await session.execute(query)
        return result.unique().scalar_one_or_none()
    
    @classmethod
    async def find_all_authors(cls, session: AsyncSession, **filter_by) -> list[Author]:
        query = (
            select(cls.model)
            .options(joinedload(cls.model.books))
            .filter_by(**filter_by)
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())