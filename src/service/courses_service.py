import uuid
import logger
from typing import List
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.student_schemas import SCourseCreate
from src.models.student_models import Course, student_course
from src.dao.base import BaseDAO





async def find_existing_courses(
    session: AsyncSession, course_titles: list[str]) -> list[Course]:
    try:
        query = select(Course).filter(Course.title.in_(course_titles))
        result = await session.execute(query)
        record = result.scalars().all()
        logger.logger.info(f"Записи {len(record)} успешно найдены в базе данных")
        return list(record)
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при поиске записей в базе данных: {e}")
        raise

 
async def create_new_courses(
    session: AsyncSession, new_course_data: list[SCourseCreate]) -> list[Course]:
    if not new_course_data:
        return []
    try:
        new_courses = [Course(**c.model_dump()) for c in new_course_data]
        session.add_all(new_courses)
        logger.logger.info(f"Записи {len(new_courses)} успешно созданы в базе данных")
        await session.flush()
        return new_courses
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при создании записей в базе данных: {e}")
        raise



async def find_or_create_courses(
    session: AsyncSession, course_data: List[SCourseCreate]) -> List[Course]:
    try:
        course_titles = [c.title for c in course_data]
        existing_courses = await find_existing_courses(session, course_titles)
        existing_titles = {c.title for c in existing_courses}
        new_course_data = [c for c in course_data if c.title not in existing_titles]
        new_courses = await create_new_courses(session, new_course_data)
        logger.logger.info(f"Записи {len(new_courses)} успешно созданы в базе данных")
        return existing_courses + new_courses
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при создании записей в базе данных: {e}")
        raise