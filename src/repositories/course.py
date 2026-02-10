from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.courses import Course

from src.schemas.courses import SCourseCreate

from src.exception.client_exception import BadRequestError, NotFoundError




async def find(session: AsyncSession, course_titles: List[str]) -> List[Course]:
    query = select(Course).filter(Course.title.in_(course_titles))
    result = await session.execute(query)
    return result.scalars().all()

async def create(session: AsyncSession, courses_data: List[SCourseCreate]) -> List[Course]:
    new_courses = [course.to_orm_model() for course in courses_data]

    session.add_all(new_courses)
    await session.flush()
    return new_courses



async def update(session: AsyncSession, course_data: List[SCourseCreate]) -> List[Course]:
    course_titles = [c.title for c in course_data]
    existing_courses = await find(session, course_titles)
    existing_titles = {c.title for c in existing_courses}
    new_course_data = [c for c in course_data if c.title not in existing_titles]
    new_courses = await create(session, new_course_data)
    return existing_courses + new_courses