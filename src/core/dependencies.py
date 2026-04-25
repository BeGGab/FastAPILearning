
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.core.redis import get_cache, RedisClient

from src.client.bio_author_client import AuthorServiceClient, get_author_service_client

from src.repositories.course import CourseRepository
from src.repositories.students import StudentRepository
from src.repositories.author import AuthorRepository
from src.repositories.user import UserRepository


from src.service.student import StudentService
from src.service.author import AuthorService
from src.service.user import UserService


async def get_author_repository(session: AsyncSession = Depends(get_async_session)) -> AuthorRepository:
    return AuthorRepository(session)

async def get_course_repository(session: AsyncSession = Depends(get_async_session)) -> CourseRepository:
    return CourseRepository(session)

async def get_student_repository(session: AsyncSession = Depends(get_async_session)) -> StudentRepository:
    return StudentRepository(session)

async def get_user_repository(session: AsyncSession = Depends(get_async_session)) -> UserRepository:
    return UserRepository(session)



async def get_author_service(
    session: AsyncSession = Depends(get_async_session),
    repository: AuthorRepository = Depends(get_author_repository),
    author_client: AuthorServiceClient = Depends(get_author_service_client),
    cache: RedisClient = Depends(get_cache)
) -> AuthorService:
    return AuthorService(session, repository, cache, author_client) 

async def get_student_service(
    session: AsyncSession = Depends(get_async_session),
    repository: StudentRepository = Depends(get_student_repository),
    course_repository: CourseRepository = Depends(get_course_repository),
    cache: RedisClient = Depends(get_cache)
) -> StudentService:
    return StudentService(session, repository, cache, course_repository)

async def get_user_service(
    session: AsyncSession = Depends(get_async_session),
    repository: UserRepository = Depends(get_user_repository),
    cache: RedisClient = Depends(get_cache)
) -> UserService:
    return UserService(session=session, repository=repository, cache=cache)

