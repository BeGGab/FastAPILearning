import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Union
from src.User.schemas_user import SUserRead, SProfileRead, SUserCreate, SProfileCreate
from src.dao.base import BaseDAO
from src.User.sessions import UserDAO
from src.User.models import User, Profile
from src.db import get_async_session




router = APIRouter()


@router.get('/healthcheck')
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}






@router.post("/users", status_code=status.HTTP_201_CREATED) #создание юзера
async def create_user_with_profile(useradd: SUserCreate, session: AsyncSession = Depends(get_async_session)) -> SUserRead:
    user = await UserDAO.create_user_with_profile(session=session, user_data=useradd.model_dump())
    return user


@router.get("/users/{id}") #Загрузка с профилем 
async def find_user_is_id(id: Union[uuid.UUID], session: AsyncSession = Depends(get_async_session)) -> SUserRead:
    user = await UserDAO.find_one_or_none_with_profile(session=session, id=id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user


@router.get("/users")
async def  find_all_users(session: AsyncSession = Depends(get_async_session)) -> List[SUserRead]:
    return await UserDAO.find_all_with_profiles(session=session)


@router.put("/update/{id}")
async def update_user_profile(id: Union[uuid.UUID], userupdate: SUserCreate, session: AsyncSession = Depends(get_async_session)) -> SUserRead:
    user = await UserDAO.update_user(session=session, user_id=id, **userupdate.model_dump())
    return user

@router.delete("/user/{id}")
async def delete_user(id: Union[uuid.UUID], session: AsyncSession = Depends(get_async_session)):
    user = await UserDAO.delete_user(session=session, user_id=id)
    return f"Пользователь {user.username} удален"
