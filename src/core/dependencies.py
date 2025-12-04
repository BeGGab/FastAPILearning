from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.service.user_service import UserDAO
from src.service.author_service import AuthorDAO
from src.service.student_service import StudentDAO


@classmethod
async def get_cls(
    cls,
    session: AsyncSession = Depends(get_async_session),
) -> UserDAO | AuthorDAO | StudentDAO:
    if cls == UserDAO:
        return UserDAO(session)
    elif cls == AuthorDAO:
        return AuthorDAO(session)
    elif cls == StudentDAO:
        return StudentDAO(session)
