import uuid
import json
import logging
from typing import List

from redress import CircuitOpenError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.redis import RedisDep

from src.schemas.user import SUserCreate, SUserRead, SUserUpdate

from src.repositories.user import UserRepository as rep_user
from src.exception.client_exception import NotFoundError, ValidationError


logger = logging.getLogger(__name__)


async def create_user_with_profile(
    session: AsyncSession,
    user_data: SUserCreate,
    redis: RedisDep
) -> SUserRead:
    user, profile = await rep_user(session).created(user_data)
    if not user:
        logger.error(f"Ошибка при создании пользователя")
        raise ValidationError(detail="Ошибка при создании пользователя")

    session.add(user)
    await session.flush()
    await session.refresh(user, ["profile"])

    user_read_data = SUserRead.model_validate(user, from_attributes=True)
    cache_key = f"user:{user.id}"
    try:
        await redis.delete(cache_key)
        await redis.setex(
            cache_key,
            3600,
            user_read_data.model_dump_json(),
        )
    except Exception as e:
        logger.warning(
            f"Не удалось обновить кэш после создания пользователя {user.id}: {e}"
        )

    return user_read_data


async def find_one_or_none_with_profile(
    session: AsyncSession, redis: RedisDep, **filter_by
) -> SUserRead:
    cache_key = f"user:{filter_by}"
    cached = await redis.get(cache_key)
    if cached:
        user_data = SUserRead.model_validate_json(cached)

    user = await rep_user(session).get_id(**filter_by)
    if not user:
        logger.error(f"Ошибка при поиске записи в базе данных")
        raise NotFoundError(detail=f"Пользователь с id {filter_by} не найден")

    user_data = SUserRead.model_validate(user, from_attributes=True)
    try:
        await redis.setex(
            cache_key,
            3600,
            user_data.model_dump_json(),
        )
    except Exception as e:
        logger.warning(f"Не удалось записать пользователя {filter_by['id']} в кэш: {e}")

    return user_data


async def find_all_with_profiles(
    session: AsyncSession, redis: RedisDep, skip: int = 0, limit: int = 100, **filter_by
) -> List[SUserRead]:
    cache_key = f"user:{filter_by, skip, limit}"
    cached_users = await redis.get(cache_key)
    if cached_users:
        return [
            SUserRead.model_validate_json(user_json)
            for user_json in json.loads(cached_users)
        ]

    users = await rep_user(session).get_all(skip, limit, **filter_by)
    if not users:
        logger.warning(
            f"Пользователи с параметрами {filter_by} не найдены, возвращен пустой список."
        )
        raise NotFoundError(detail=f"Пользователи с параметрами {filter_by} не найдены")
    try:
        users_json = json.dumps(
            [
                SUserRead.model_validate(rec, from_attributes=True).model_dump_json()
                for rec in users
            ]
        )
        await redis.setex(cache_key, 3600, users_json)
    except Exception as e:
        logger.warning(f"Не удалось записать пользователей в кэш: {e}")

    return [SUserRead.model_validate(rec, from_attributes=True) for rec in users]


async def update_user(
    session: AsyncSession, redis: RedisDep, user_id: uuid.UUID, data: SUserUpdate
) -> SUserRead:
    user = await rep_user(session).update(user_id, data)
    if not user:
        logger.error(f"Ошибка при поиске записи в базе данных")
        raise NotFoundError(detail=f"Пользователь с id {user_id} не найден")

    await session.flush()
    await session.refresh(user, ["profile"])

    cache_key = f"user:{user_id}"
    try:
        await redis.delete(cache_key)
        await redis.setex(
            cache_key,
            3600,
            SUserRead.model_validate(user, from_attributes=True).model_dump_json(),
        )
    except Exception as e:
        logger.warning(
            f"Не удалось обновить кэш после изменения пользователя {user_id}: {e}"
        )

    return SUserRead.model_validate(user, from_attributes=True)


async def delete_user(session: AsyncSession, redis: RedisDep, user_id: uuid.UUID):
    user = await rep_user(session).get_id(id=user_id)
    if not user:
        logger.error(f"Ошибка при удалении записи из базы данных")
        raise NotFoundError(detail=f"Пользователь с id {user_id} не найден")
    await session.delete(user)

    try:
        await redis.delete(f"user:{user_id}")
    except Exception as e:
        logger.warning(f"Не удалось удалить ключ кэша пользователя {user_id}: {e}")
