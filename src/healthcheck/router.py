from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any
from src.models.schemas import SUserAdd, SUser
from src.models.sessions import UserDAO
from src.models.rb import RBUser
from src.db import get_async_session




router = APIRouter()


@router.get('/healthcheck')
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}






@router.get("/users/{user_id}", tags=["users"], description="Получить юзера по id")
async def get_user_by_id(user_id: int, session: AsyncSession = Depends(get_async_session)) -> SUser:
    user = await UserDAO.find_one_or_none_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/users", tags=["users"], description="Создать юзера")
async def add_user(
    user: SUserAdd, session: AsyncSession = Depends(get_async_session)
) -> SUser:
    try:
        new_user = await UserDAO.add_user_with_profile(session, **user.model_dump())
    except Exception:
        # Здесь лучше логгировать ошибку
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при создании пользователя")
    return new_user
