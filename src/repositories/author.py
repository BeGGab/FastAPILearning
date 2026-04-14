import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.author import Author

from src.schemas.author import SAuthorCreate, SAuthorUpdate


class AuthorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def created(self, author_data: SAuthorCreate) -> Author:
        author, books = author_data.to_orm_models()
        return author, books

    async def get_id(self, **filter_by) -> Optional[Author]:
        query = select(Author).options(joinedload(Author.books)).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.unique().scalar()

    async def get_all(
        self, skip: int = 0, limit: int = 100, **filter_by
    ) -> List[Author]:
        query = (
            select(Author)
            .options(joinedload(Author.books))
            .filter_by(**filter_by)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def update(self, author_id: uuid.UUID, author_data: SAuthorUpdate) -> Author:
        author = await self.get_id(id=author_id)
        author_data.apply_updates(author)
        return author
