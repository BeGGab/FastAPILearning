import uuid
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from typing import List

from src.schemas.user import SUserRead, SUserCreate, SUserUpdate
from src.service.user import UserService
from src.core.dependencies import get_user_service

router = APIRouter(prefix="/api/v1/users_profiles", tags=["user"])


@router.get("/", status_code=status.HTTP_200_OK)
async def find_all_users(
    user_service: UserService = Depends(get_user_service),
    skip: int = 0,
    limit: int = 100,
) -> List[SUserRead]:
    return await user_service.find_all_with_profiles(skip=skip, limit=limit)


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def find_user_is_id(
    user_id: uuid.UUID, 
    user_service: UserService = Depends(get_user_service),
) -> SUserRead:
    return await user_service.find_one_or_none_with_profile(
        user_id=user_id,
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_user_with_profile(
    payload: SUserCreate, 
    user_service: UserService = Depends(get_user_service),
) -> SUserRead:
    return await user_service.create_user_with_profile(user_data=payload)


@router.put("/{user_id}", status_code=status.HTTP_200_OK)
async def update_user_profile(
    user_id: uuid.UUID,
    payload: SUserUpdate,
    user_service: UserService = Depends(get_user_service),
) -> SUserRead:
    return await user_service.update_user(user_id=user_id, data=payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_users(
    user_id: uuid.UUID, 
    user_service: UserService = Depends(get_user_service),
):
    await user_service.delete_user(user_id=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
