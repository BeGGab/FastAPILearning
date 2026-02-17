import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.courses import SCourseCreate, SCourseRead

from src.repositories.course import CourseRepository as rep

from src.exception.client_exception import BadRequestError, NotFoundError

logger = logging.getLogger(__name__)


async def find_all_courses(
    session: AsyncSession, skip: int = 0, limit: int = 100
) -> List[SCourseRead]:
    course_orm = await rep(session).get_all(skip, limit)
    if not course_orm:
        logger.warning("Курсы не найдены, возвращен пустой список.")
        return []
    return [
        SCourseRead.model_validate(course, from_attributes=True)
        for course in course_orm
    ]


async def find_existing_courses(
    session: AsyncSession, course_titles: List[str]
) -> List[SCourseRead]:
    course_orm = await rep(session).find(course_titles)
    if not course_orm:
        logger.error(f"Ошибка при поиске записи в базе данных")
        raise NotFoundError(detail=f"Курсы с параметрами {course_titles} не найдены")
    return [
        SCourseRead.model_validate(course, from_attributes=True)
        for course in course_orm
    ]


async def create_new_courses(
    session: AsyncSession, new_course_data: List[SCourseCreate]
) -> List[SCourseRead]:
    new_courses = await rep(session).create(new_course_data)
    if not new_courses:
        logger.error(f"Ошибка при создании курса")
        raise BadRequestError(detail="Ошибка при создании курса")

    await session.flush()
    return [
        SCourseRead.model_validate(course, from_attributes=True)
        for course in new_courses
    ]


async def update_courses(
    session: AsyncSession, course_data: List[SCourseCreate]
) -> List[SCourseRead]:
    update_courses = await rep(session).update(course_data)
    if not update_courses:
        logger.error(f"Ошибка при обновлении курса")
        raise BadRequestError(detail="Ошибка при обновлении курса")
    return [
        SCourseRead.model_validate(course, from_attributes=True)
        for course in update_courses
    ]


async def delete_courses(session: AsyncSession, name: str = None):
    courses = await rep(session).find(course_titles=[name])
    if not courses:
        logger.error(f"Ошибка при удалении записи из базы данных")
        raise NotFoundError(detail=f"Курсы с параметрами {name} не найдены")
    for course in courses:
        await session.delete(course)
