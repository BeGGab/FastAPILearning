import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from src.dao.schemas import SUserRead, SUserCreate
from src.dao.service import UserDAO

from src.db import get_async_session




router = APIRouter(tags=["user"])



@router.get("/users")
async def  find_all_users(session: AsyncSession = Depends(get_async_session)) -> List[SUserRead]:
    return await UserDAO.find_all_with_profiles(session=session)


@router.get("/users/{id}") 
async def find_user_is_id(id: uuid.UUID, session: AsyncSession = Depends(get_async_session)) -> SUserRead:
    user = await UserDAO.find_one_or_none_with_profile(session=session, id=id)
    return user


@router.post("/users",)
async def create_user_with_profile(useradd: SUserCreate, session: AsyncSession = Depends(get_async_session)) -> SUserRead:
    user = await UserDAO.create_user_with_profile(session=session, user_data=useradd.model_dump())
    return user


@router.put("/users/{id}")
async def update_user_profile(id: uuid.UUID, userupdate: SUserCreate, session: AsyncSession = Depends(get_async_session)) -> SUserRead:
    user = await UserDAO.update_user(session=session, user_id=id, **userupdate.model_dump())
    return user

@router.delete("/users/{id}")
async def delete_user(id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    user = await UserDAO.delete_user(session=session, user_id=id)
    return f"Пользователь {user.username} удален"
