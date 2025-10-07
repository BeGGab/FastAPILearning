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
async def get_user_by_id(user_id: int, session: AsyncSession = Depends(get_async_session)) -> dict[str, str]:
    return await UserDAO.find_one_or_none_by_id(session, user_id)


@router.post("/users", tags=["users"], description="Создать юзера")
async def add_user(session: AsyncSession = Depends(get_async_session), user: SUserAdd = Depends()) -> Dict[SUser]:
    check = await UserDAO.add_user_with_profile(session, **user.to_dict())
    if check:
        return {'message': 'Пользователь успешно создан', 'data': check}
    else:
        return {'message': 'Ошибка при создании пользователя'}







