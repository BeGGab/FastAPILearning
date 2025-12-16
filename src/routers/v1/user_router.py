import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from src.core.enums import Status
from src.schemas.user_schemas import SUserRead, SUserCreate
from src.service.user_service import (
    create_user_with_profile,
    find_one_or_none_with_profile,
    find_all_with_profiles,
    update_user,
    delete_user,
)

from src.core.db import get_async_session


router = APIRouter(tags=["user"])


@router.get("/users")
async def find_all_users(
    session: AsyncSession = Depends(get_async_session),
) -> List[SUserRead]:
    return await find_all_with_profiles(session=session)


@router.get("/users/{id}")
async def find_user_is_id(
    id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
) -> SUserRead:
    user = await find_one_or_none_with_profile(session=session, id=id)
    return user


@router.post(
    "/users",
)
async def add_user_with_profile(
    payload: SUserCreate, session: AsyncSession = Depends(get_async_session)
) -> SUserRead:
    user = await create_user_with_profile(session=session, user_data=payload)
    return user


@router.put("/users/{id}")
async def update_user_profile(
    id: uuid.UUID,
    payload: SUserCreate,
    session: AsyncSession = Depends(get_async_session),
) -> SUserRead:
    user = await update_user(session=session, user_id=id, data=payload)
    return user


@router.delete("/users/{id}")
async def delete_users(
    id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
):
    user = await delete_user(session=session, user_id=id)
    return Status.DELETED
