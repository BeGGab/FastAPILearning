import uuid
import logging
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.courses import SCourseCreate, SCourseRead
from src.models.courses import Course
from src.exception.client_exception import NotFoundError

logger = logging.getLogger(__name__)



async def find_existing_courses(
    session: AsyncSession, course_titles: List[str]
) -> List[SCourseRead]:
    query = select(Course).filter(Course.title.in_(course_titles))
    result = await session.execute(query)
    records = result.scalars().all()
    return [SCourseRead.model_validate(rec, from_attributes=True) for rec in records]




async def create_new_courses(
    session: AsyncSession, new_course_data: List[SCourseCreate]
) -> List[Course]:
    new_courses= [c.to_orm_model() for c in new_course_data]

    session.add_all(new_courses)
    await session.flush()
    return new_courses




async def update_courses(
    session: AsyncSession, course_data: List[SCourseCreate]
) -> List[Course]:
    course_titles = [c.title for c in course_data]
    existing_courses = await find_existing_courses(session, course_titles)
    existing_titles = {c.title for c in existing_courses}
    new_course_data = [c for c in course_data if c.title not in existing_titles]
    new_courses = await create_new_courses(session, new_course_data)
    return existing_courses + new_courses