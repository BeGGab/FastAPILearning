import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from src.core.enums import Status
from src.schemas.user_schemas import SUserRead, SUserCreate, SUserUpdate
from src.service.user_service import (
    create_user_with_profile,
    find_one_or_none_with_profile,
    find_all_with_profiles,
    update_user,
    delete_user,
)

from src.core.db import get_async_session


router = APIRouter(prefix="/api/v1/users_profiles", tags=["user"])


@router.get("/", status_code=status.HTTP_200_OK)
async def find_all_users(
    session: AsyncSession = Depends(get_async_session),
) -> List[SUserRead]:
    return await find_all_with_profiles(session=session)


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def find_user_is_id(
    id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
) -> SUserRead:
    return await find_one_or_none_with_profile(session=session, id=id)
    


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_user_with_profile(
    payload: SUserCreate, session: AsyncSession = Depends(get_async_session)
) -> SUserRead:
    return await create_user_with_profile(session=session, user_data=payload)
    


@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_user_profile(
    id: uuid.UUID,
    payload: SUserUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> SUserRead:
    return await update_user(session=session, user_id=id, data=payload)
    


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_users(
    id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
):
    await delete_user(session=session, user_id=id)
    return Status.DELETED
