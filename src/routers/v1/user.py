import uuid
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from src.core.enums import Status
from src.schemas.user import SUserRead, SUserCreate, SUserUpdate
from src.service.user import UserService

from src.core.db import get_async_session
from src.core.redis import RedisDep


router = APIRouter(prefix="/api/v1/users_profiles", tags=["user"])


@router.get("/", status_code=status.HTTP_200_OK)
async def find_all_users(
    redis: RedisDep,
    session: AsyncSession = Depends(get_async_session),
    skip: int = 0,
    limit: int = 100,
) -> List[SUserRead]:
    return await UserService(session, redis).find_all_with_profiles(skip=skip, limit=limit)


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def find_user_is_id(
    user_id: uuid.UUID, 
    redis: RedisDep,
    session: AsyncSession = Depends(get_async_session)
) -> SUserRead:
    return await UserService(session, redis).find_one_or_none_with_profile(
        user_id=user_id,
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_user_with_profile(
    payload: SUserCreate, 
    redis: RedisDep,
    session: AsyncSession = Depends(get_async_session),
) -> SUserRead:
    return await UserService(session, redis).create_user_with_profile(user_data=payload)


@router.put("/{user_id}", status_code=status.HTTP_200_OK)
async def update_user_profile(
    user_id: uuid.UUID,
    payload: SUserUpdate,
    redis: RedisDep,
    session: AsyncSession = Depends(get_async_session)
) -> SUserRead:
    return await UserService(session, redis).update_user(user_id=user_id, data=payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_users(
    user_id: uuid.UUID, 
    redis: RedisDep,
    session: AsyncSession = Depends(get_async_session)
):
    await UserService(session, redis).delete_user(user_id=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
