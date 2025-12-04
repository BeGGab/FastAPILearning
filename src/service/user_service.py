import uuid
from typing import List
from sqlalchemy import select, update, delete, event, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user_schemas import (
    SUserCreate,
    SUserRead,
    SProfileCreate,
    SProfileRead,
)
from src.models.user_models import User, Profile
from src.dao.base import BaseDAO


class UserDAO(BaseDAO):
    model = User


    @classmethod
    async def create_user_with_profile(cls, session: AsyncSession, user_data: dict) -> User:        
        profile_data = user_data.pop("profile")
        user = User(
            **user_data,
            profile=Profile(**profile_data)
        )
        session.add(user)
        await session.flush()
        await session.refresh(user, ["profile"])
        return user

    @classmethod
    async def find_one_or_none_with_profile(
        cls, session: AsyncSession, **filter_by) -> User:
        query = (
            select(cls.model)
            .options(joinedload(cls.model.profile))
            .filter_by(**filter_by)
        )
        result = await session.execute(query)
        return result.scalar()

    @classmethod
    async def find_all_with_profiles(
        cls, session: AsyncSession, **filter_by) -> list[User]:
        query = (
            select(cls.model)
            .options(joinedload(cls.model.profile))
            .filter_by(**filter_by)
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def update_user(
        cls, session: AsyncSession, user_id: uuid.UUID, **Values) -> User:
        profile_data = Values.pop("profile", None)

        user_update_query = (
            update(cls.model).where(cls.model.id == user_id).values(**Values)
        )
        if profile_data:
            profile_update_query = (
                update(Profile).where(Profile.user_id == user_id).values(**profile_data)
            )
            await session.execute(profile_update_query)

        await session.execute(user_update_query)

        updated_user = await cls.find_one_or_none_with_profile(
            session=session, id=user_id
        )
        return updated_user

    @classmethod
    async def delete_user(cls, session: AsyncSession, user_id: uuid.UUID):
        user = await cls.find_one_or_none_with_profile(session, id=user_id)
        if not user:
            return {"error": "User not found"}

        await session.delete(user)
        return user
