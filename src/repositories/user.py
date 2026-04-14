from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User

from src.schemas.user import SUserCreate, SUserUpdate, SUserRead


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def created(self, user_data: SUserCreate) -> User:
        user, profile = user_data.to_orm_models()
        return user, profile

    async def get_id(self, **filter_by) -> Optional[User]:
        query = select(User).options(joinedload(User.profile)).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.unique().scalar()

    async def get_all(self, skip: int = 0, limit: int = 100, **filter_by) -> List[User]:
        query = (
            select(User)
            .options(joinedload(User.profile))
            .filter_by(**filter_by)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, user_id: int, user_data: SUserUpdate) -> User:
        user = await self.get_id(id=user_id)
        user_data.apply_to_user(user)
        return user

    def apply_bio_data_to_user(
        self, user_data: SUserRead, bio_data: Optional[dict]
    ) -> SUserRead:
        if not bio_data:
            return user_data
        return user_data.model_copy(
            update={
                "bio_text": bio_data.get("text"),
                "year_of_birth": bio_data.get("year_of_birth"),
            }
        )
