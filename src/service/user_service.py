import uuid
import logging
from typing import List
from sqlalchemy import select, update, delete, event, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user_schemas import (
    SUserCreate,
    SUserRead,
    SUserUpdate,
    SProfileCreate,
    SProfileRead,
)
from src.models.user_models import User, Profile
from src.exception.base import NotFoundError
from src.dao.base import BaseDAO


logger = logging.getLogger(__name__)


async def create_user_with_profile(
    session: AsyncSession, user_data: SUserCreate
) -> User:
    try:
        user, profile = user_data.to_orm_models()
        session.add(user)
        if profile:
            session.add(profile)

        logger.info(f"Запись {user.username} успешно добавлена в базу данных")
        await session.flush()
        await session.refresh(user, ["profile"])
        return user
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении записи в базу данных: {e}")
        raise


async def find_one_or_none_with_profile(session: AsyncSession, **filter_by) -> User:
    try:
        query = select(User).options(joinedload(User.profile)).filter_by(**filter_by)
        result = await session.execute(query)
        user = result.scalar()
        if not user:
            raise NotFoundError(f"Пользователь с параметрами {filter_by} не найден")
        logger.info(f"Запись {filter_by} успешно найдена в базе данных")
        return user
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при поиске записи в базе данных: {e}")
        raise


async def find_all_with_profiles(session: AsyncSession, **filter_by) -> list[User]:
    try:
        query = select(User).options(joinedload(User.profile)).filter_by(**filter_by)
        result = await session.execute(query)
        record = result.scalars().all()
        logger.info(f"Записи {len(record)} успешно найдены в базе данных")
        return list(record)
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при поиске записей в базе данных: {e}")
        raise


async def update_user(
    session: AsyncSession, user_id: uuid.UUID, data: SUserUpdate) -> User:
    try:
        user = await find_one_or_none_with_profile(session=session, id=user_id) # NotFoundError будет вызван внутри
        logger.info(f"Найден пользователь: {user.username}")

        # Вся логика обновления в схеме
        data.apply_to_user(user)

        logger.info(f"Данные пользователя {user.username} обновлены")
        await session.flush()
        await session.refresh(user, ["profile"])
        return user

    except ValueError as e:
        logger.warning(f"Ошибка валидации: {e}")
        raise
    except SQLAlchemyError as e:
        logger.error(f"Ошибка БД: {e}")
        raise


async def delete_user(session: AsyncSession, user_id: uuid.UUID):
    user = await find_one_or_none_with_profile(session, id=user_id)
    try:
        await session.delete(user)
        logger.info(f"Запись {user.username} успешно удалена из базы данных")
        return user
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при удалении записи из базы данных: {e}")
        raise
