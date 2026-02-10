from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.author import Author


async def get_id(session: AsyncSession, **filter_by) -> Optional[Author]:
    query = select(Author).options(joinedload(Author.books)).filter_by(**filter_by)
    result = await session.execute(query)
    return result.unique().scalar()


async def get_all(session: AsyncSession, skip: int = 0, limit: int = 100, **filter_by) -> List[Author]:
    query = select(Author).options(joinedload(Author.books)).filter_by(**filter_by).offset(skip).limit(limit)
    result = await session.execute(query)
    return result.unique().scalars().all()