import uuid
import logging
from typing import List
from sqlalchemy import select, update, delete, event, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user_schemas import (
    SUserCreate,
    SUserRead,
    SUserUpdate
)
from src.models.user_models import User
from src.exception.client_exception import BadRequestError
from src.exception.business import UserNotFoundError


logger = logging.getLogger(__name__)


async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> User:
    query = select(User).options(joinedload(User.profile)).filter_by(id=user_id)
    result = await session.execute(query)
    user = result.scalar()
    if not user:
        logger.error(f"Пользователь с id {user_id} не найден")
        raise UserNotFoundError(user_id=user_id)
    return user


async def create_user_with_profile(
    session: AsyncSession, user_data: SUserCreate
) -> SUserRead:
    try:
        user, profile = user_data.to_orm_models()

        session.add(user)
        await session.flush()
        await session.refresh(user, ["profile"])
        return SUserRead.model_validate(user, from_attributes=True)
    except IntegrityError as e:
        raise BadRequestError(detail=str(e))


async def find_one_or_none_with_profile(
    session: AsyncSession, **filter_by
) -> SUserRead:
    query = select(User).options(joinedload(User.profile)).filter_by(**filter_by)
    result = await session.execute(query)
    user = result.scalar()
    if not user:
        logger.error(f"Ошибка при поиске записи в базе данных")
        raise UserNotFoundError(detail=f"Пользователь с параметрами {filter_by} не найден")
    return SUserRead.model_validate(user, from_attributes=True)


async def find_all_with_profiles(session: AsyncSession, **filter_by) -> List[SUserRead]:
    query = select(User).options(joinedload(User.profile)).filter_by(**filter_by)
    result = await session.execute(query)
    records = result.scalars().all()
    if not records:
        logger.warning(
            f"Пользователи с параметрами {filter_by} не найдены, возвращен пустой список."
        )
        raise UserNotFoundError(detail=f"Пользователи с параметрами {filter_by} не найдены")
    return [SUserRead.model_validate(rec, from_attributes=True) for rec in records]


async def update_user(
    session: AsyncSession, user_id: uuid.UUID, data: SUserUpdate
) -> SUserRead:
    user = await get_user_by_id(session=session, user_id=user_id)
    if not user:
        logger.error(f"Ошибка при поиске записи в базе данных")
        raise UserNotFoundError(user_id=user_id)
    try:
        data.apply_to_user(user)

        await session.flush()
        await session.refresh(user, ["profile"])
        return SUserRead.model_validate(user, from_attributes=True)
    except IntegrityError as e:
        raise BadRequestError(detail=str(e))


async def delete_user(session: AsyncSession, user_id: uuid.UUID):
    user = await get_user_by_id(session=session, user_id=user_id)
    if not user:
        logger.error(f"Ошибка при удалении записи из базы данных")
        raise UserNotFoundError(user_id=user_id)
    await session.delete(user)
