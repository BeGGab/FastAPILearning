from sqlalchemy import select, update, delete, event, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from dao.base import BaseDAO
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.models import User, Profile
from src.models.schemas import SUserAdd, SProfileAdd






class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def add_user_with_profile(cls, session: AsyncSession, user_data: dict[str, str]) -> SUserAdd:
        async with session.begin():
            try:
                profile_data = user_data.pop("profile")
                user = User(**user_data)
                session.add(user)
                await session.flush()
                profile = Profile(**profile_data)
                profile.user_id = user.id
                session.add(profile)
                print(f"Создан пользователь с id: {user.id} и ему присвоен профилем с id: {profile.id}")
                return {"user_id": user.id, "profile_id": profile.id}
            except SQLAlchemyError as e:
                raise e




                