from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.courses import Course

from src.schemas.courses import SCourseCreate



class CourseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find(self, course_titles: List[str]) -> List[Course]:
        query = select(Course).filter(Course.title.in_(course_titles))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Course]:
        query = select(Course).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(
        self, courses_data: List[SCourseCreate]
    ) -> List[Course]:
        new_courses = [course.to_orm_model() for course in courses_data]

        self.session.add_all(new_courses)
        await self.session.flush()
        return new_courses

    async def update(
        self, course_data: List[SCourseCreate]
    ) -> List[Course]:
        course_titles = [c.title for c in course_data]
        existing_courses = await self.find(course_titles)
        existing_titles = {c.title for c in existing_courses}
        new_course_data = [c for c in course_data if c.title not in existing_titles]
        new_courses = []
        if new_course_data:
            new_courses = await self.create(new_course_data)
        return existing_courses + new_courses
