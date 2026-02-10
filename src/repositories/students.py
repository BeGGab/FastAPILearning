import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.student import Student


async def get_id(session: AsyncSession, student_id: uuid.UUID) -> Optional[Student]:
    query = (
        select(Student).options(joinedload(Student.courses)).filter_by(id=student_id)
    )
    result = await session.execute(query)
    return result.unique().scalar()


async def get_all(
    session: AsyncSession, skip: int = 0, limit: int = 100, **filter_by
) -> List[Student]:
    query = (
        select(Student)
        .options(joinedload(Student.courses))
        .filter_by(**filter_by)
        .offset(skip)
        .limit(limit)
    )
    result = await session.execute(query)
    return result.unique().scalars().all()
