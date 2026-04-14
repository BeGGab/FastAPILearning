import uuid
import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user import SUserCreate, SUserRead, SUserUpdate

from src.repositories.user import UserRepository as rep_user
from src.exception.client_exception import NotFoundError, ValidationError


logger = logging.getLogger(__name__)


async def create_user_with_profile(
    session: AsyncSession, user_data: SUserCreate
) -> SUserRead:
    user, profile = await rep_user(session).created(user_data)
    if not user:
        logger.error(f"Ошибка при создании пользователя")
        raise ValidationError(detail="Ошибка при создании пользователя")

    session.add(user)
    await session.flush()
    await session.refresh(user, ["profile"])
    return SUserRead.model_validate(user, from_attributes=True)


async def find_one_or_none_with_profile(
    session: AsyncSession, **filter_by
) -> SUserRead:
    user = await rep_user(session).get_id(**filter_by)
    if not user:
        logger.error(f"Ошибка при поиске записи в базе данных")
        raise NotFoundError(detail=f"Пользователь с id {filter_by} не найден")
    return SUserRead.model_validate(user, from_attributes=True)


async def find_all_with_profiles(
    session: AsyncSession, skip: int = 0, limit: int = 100, **filter_by
) -> List[SUserRead]:
    users = await rep_user(session).get_all(skip, limit, **filter_by)
    if not users:
        logger.warning(
            f"Пользователи с параметрами {filter_by} не найдены, возвращен пустой список."
        )
        raise NotFoundError(detail=f"Пользователи с параметрами {filter_by} не найдены")
    return [SUserRead.model_validate(rec, from_attributes=True) for rec in users]


async def update_user(
    session: AsyncSession, user_id: uuid.UUID, data: SUserUpdate
) -> SUserRead:
    user = await rep_user(session).update(user_id, data)
    if not user:
        logger.error(f"Ошибка при поиске записи в базе данных")
        raise NotFoundError(detail=f"Пользователь с id {user_id} не найден")

    await session.flush()
    await session.refresh(user, ["profile"])
    return SUserRead.model_validate(user, from_attributes=True)


async def delete_user(session: AsyncSession, user_id: uuid.UUID):
    user = await rep_user(session).get_id(id=user_id)
    if not user:
        logger.error(f"Ошибка при удалении записи из базы данных")
        raise NotFoundError(detail=f"Пользователь с id {user_id} не найден")
    await session.delete(user)
