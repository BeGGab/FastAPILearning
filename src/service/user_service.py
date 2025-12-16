import uuid
from typing import List
from sqlalchemy import select, update, delete, event, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import logger

from src.schemas.user_schemas import (
    SUserCreate,
    SUserRead,
    SUserUpdate,
    SProfileCreate,
    SProfileRead,
)
from src.models.user_models import User, Profile
from src.dao.base import BaseDAO


async def create_user_with_profile(session: AsyncSession, user_data: SUserCreate) -> User:
    try:
        user_dict = user_data.model_dump()
        profile_data = user_dict.pop("profile", None)
        user = User(**user_dict)
        if profile_data:
            user.profile = Profile(**profile_data)
        session.add(user)
        logger.logger.info(f"Запись {user.username} успешно добавлена в базу данных")
        await session.flush()
        await session.refresh(user, ["profile"])
        return user 
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при добавлении записи в базу данных: {e}")
        raise 
    


async def find_one_or_none_with_profile(session: AsyncSession, **filter_by) -> User:
    try:
        query = select(User).options(joinedload(User.profile)).filter_by(**filter_by)
        result = await session.execute(query)
        logger.logger.info(f"Запись {filter_by} успешно найдена в базе данных")
        return result.scalar()
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при поиске записи в базе данных: {e}")
        raise




async def find_all_with_profiles(session: AsyncSession, **filter_by) -> list[User]:
    try:
        query = select(User).options(joinedload(User.profile)).filter_by(**filter_by)
        result = await session.execute(query)
        record = result.scalars().all()
        logger.logger.info(f"Записи {len(record)} успешно найдены в базе данных")
        return list(record)
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при поиске записей в базе данных: {e}")
        raise



async def update_user(
    session: AsyncSession, user_id: uuid.UUID, data: SUserUpdate
) -> User:
    try:
        user = await find_one_or_none_with_profile(session=session, id=user_id)
        logger.logger.info(f"Запись {user.username} успешно найдена в базе данных")

        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        if "profile" in update_data:
            profile_data = update_data.pop("profile")
            if user.profile:
                for key, value in profile_data.items():
                    setattr(user.profile, key, value)

        for key, value in update_data.items():
            setattr(user, key, value)

        logger.logger.info(f"Запись {update_data.items()} успешно обновлена в базе данных")
        await session.flush()
        return user
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при обновлении записи в базе данных: {e}")
        raise


async def delete_user(session: AsyncSession, user_id: uuid.UUID):
    user = await find_one_or_none_with_profile(session, id=user_id)
    logger.logger.info(f"Запись {user.username} успешно найдена в базе данных")
    if not user:
        raise ValueError(f"Пользователь с id {user_id} не найден")
    try:
        await session.delete(user)
        logger.logger.info(f"Запись {user.username} успешно удалена из базы данных")
        return user
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при удалении записи из базы данных: {e}")
        raise