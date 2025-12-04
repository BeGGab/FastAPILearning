import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.student_schemas import SStudentCreate, SCourseCreate
from src.models.student_models import Student, Course, student_course
from src.dao.base import BaseDAO


class StudentDAO(BaseDAO):
    model = Student
        


    @classmethod
    async def add_student(
        cls, session: AsyncSession, student_data: SStudentCreate) -> Student:
        db_data = student_data.prepare_db_data()
        student = Student(**db_data)
        student.courses = await cls.find_or_create_courses(session, student_data.courses)

        session.add(student)
        await session.flush()
        await session.refresh(student, ["courses"])
        return student

    @classmethod
    async def find_all_students(
        cls,session: AsyncSession, **filter_by) -> List[Student]:
        query = (
            select(cls.model)
            .options(joinedload(cls.model.courses))
            .filter_by(**filter_by)
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    @classmethod
    async def find_one_with_id(cls, session: AsyncSession, id: uuid.UUID) -> Student:
        query = (
            select(cls.model).options(joinedload(cls.model.courses)).filter_by(id=id)
        )
        result = await session.execute(query)
        return result.scalar()

    @classmethod
    async def _find_existing_courses(
        cls, session: AsyncSession, course_titles: list[str]
    ) -> list[Course]:
        if not course_titles:
            return []
        query = select(Course).filter(Course.title.in_(course_titles))
        result = await session.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def _create_new_courses(
        cls, session: AsyncSession, new_course_data: list[SCourseCreate]
    ) -> list[Course]:
        if not new_course_data:
            return []
        new_courses = [Course(**c.model_dump()) for c in new_course_data]
        session.add_all(new_courses)
        await session.flush()
        return new_courses

    @classmethod
    async def find_or_create_courses(
        cls, session: AsyncSession, course_data: List[SCourseCreate]) -> List[Course]:
        course_titles = [c.title for c in course_data]
        existing_courses = await cls._find_existing_courses(session, course_titles)
        existing_titles = {c.title for c in existing_courses}
        new_course_data = [c for c in course_data if c.title not in existing_titles]
        new_courses = await cls._create_new_courses(session, new_course_data)
        return existing_courses + new_courses

    @classmethod
    async def update_student_with_course(
        cls, session: AsyncSession, student_id: uuid.UUID, student_data: SStudentCreate
    ) -> Student:
        student = await cls.find_one_with_id(session=session, id=student_id)
        if not student:
            raise ValueError(f"Студент с id {student_id} не найден")

        student.name = student_data.name
        student.courses = await cls.find_or_create_courses(
            session, student_data.courses
        )
        await session.refresh(student, attribute_names=["courses"])
        return student
