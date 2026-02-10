import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User




async def get_id(session: AsyncSession, **filter_by) -> Optional[User]:
    query = select(User).options(joinedload(User.profile)).filter_by(**filter_by)
    result = await session.execute(query)
    return result.unique().scalar()

async def get_all(session: AsyncSession, **filter_by) -> List[User]:
    query = select(User).options(joinedload(User.profile)).filter_by(**filter_by)
    result = await session.execute(query)
    return result.scalars().all()
