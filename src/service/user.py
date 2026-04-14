import uuid
import ujson
import logging
import redress 
from typing import List, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.redis import RedisDep

from src.core.config import Settings

from src.schemas.user import SUserCreate, SUserRead, SUserUpdate

from src.repositories.user import UserRepository as rep_user
from src.exception.client_exception import NotFoundError, ValidationError


logger = logging.getLogger(__name__)

settings = Settings()


class UserService:
    def __init__(self, session: AsyncSession, redis: RedisDep):
        self.session = session
        self.redis = redis

    @redress.retry(max_attempts=3, deadline_s=10, strategy=redress.strategies.decorrelated_jitter(max_s=5.0))
    async def set_cache(self, key: str, value: Any, ttl: int):
        await self.redis.setex(key, ttl, value)

    async def create_user_with_profile(
        self, user_data: SUserCreate
    ) -> SUserRead:
        user, profile = await rep_user(self.session).created(user_data)
        if not user:
            logger.error(f"Ошибка при создании пользователя")
            raise ValidationError(detail="Ошибка при создании пользователя")

        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user, ["profile"])

        user_read_data = SUserRead.model_validate(user, from_attributes=True)
        cache_key = f"user:{user.id}"
        await self.set_cache(cache_key, user_read_data.model_dump_json(), settings.ttl)

        return user_read_data


    async def find_one_or_none_with_profile(
        self, **filter_by
    ) -> SUserRead:
        cache_key = f"user:{filter_by}"
        cached = await self.redis.get(cache_key)
        if cached:
            user_data = SUserRead.model_validate_json(cached)

        user = await rep_user(self.session).get_id(**filter_by)
        if not user:
            logger.error(f"Ошибка при поиске записи в базе данных")
            raise NotFoundError(detail=f"Пользователь с id {filter_by} не найден")

        user_data = SUserRead.model_validate(user, from_attributes=True)
        await self.set_cache(cache_key, user_data.model_dump_json(), settings.ttl)

        return user_data


    async def find_all_with_profiles(
        self, skip: int = 0, limit: int = 100, **filter_by
    ) -> List[SUserRead]:
        cache_key = f"user:{filter_by, skip, limit}"
        cached_users = await self.redis.get(cache_key)
        if cached_users:
            return [
                SUserRead.model_validate_json(user_json)
                for user_json in ujson.loads(cached_users)
            ]

        users = await rep_user(self.session).get_all(skip, limit, **filter_by)
        if not users:
            logger.warning(
                f"Пользователи с параметрами {filter_by} не найдены, возвращен пустой список."
            )
            raise NotFoundError(detail=f"Пользователи с параметрами {filter_by} не найдены")
        users_json = ujson.dumps(
            [
                SUserRead.model_validate(rec, from_attributes=True).model_dump_json()
                for rec in users
            ]
        )
        await self.set_cache(cache_key, users_json, settings.ttl)

        return [SUserRead.model_validate(rec, from_attributes=True) for rec in users]


    async def update_user(
        self, user_id: uuid.UUID, data: SUserUpdate
    ) -> SUserRead:
        user = await rep_user(self.session).update(user_id, data)
        if not user:
            logger.error(f"Ошибка при поиске записи в базе данных")
            raise NotFoundError(detail=f"Пользователь с id {user_id} не найден")

        await self.session.flush()
        await self.session.refresh(user, ["profile"])

        cache_key = f"user:{user_id}"
        await self.set_cache(cache_key, SUserRead.model_validate(user, from_attributes=True).model_dump_json(), settings.ttl)

        return SUserRead.model_validate(user, from_attributes=True)


    async def delete_user(self, user_id: uuid.UUID):
        user = await rep_user(self.session).get_id(id=user_id)
        if not user:
            logger.error(f"Ошибка при удалении записи из базы данных")
            raise NotFoundError(detail=f"Пользователь с id {user_id} не найден")
        await self.session.delete(user)

        await self.redis.delete(f"user:{user_id}")
