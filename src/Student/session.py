import uuid
from typing import List
from sqlalchemy import select, update, delete, event, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.student.models import Student, Course, student_course
from src.dao.base import BaseDAO





class StudentDAO(BaseDAO):
    model = Student



    @classmethod
    async def add_student(cls, session: AsyncSession, student_data: dict) -> Student:
        course_data = student_data.pop("courses", [])
        student = Student(**student_data)
        if course_data:
            student.courses = [Course(**course) for course in course_data]
        session.add(student)
        await session.commit()
        await session.refresh(student, ["courses"])
        return student
    
    @classmethod
    async def find_all_students(cls, session: AsyncSession, **filter_by) -> List[Student]:
        query = (
            select(cls.model)
            .options(joinedload(cls.model.courses))
            .filter_by(**filter_by)
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())
    

    @classmethod
    async def find_one_with_id(cls, session: AsyncSession, id: uuid.UUID) -> Student | None:
        query = (
            select(cls.model)
            .options(joinedload(cls.model.courses))
            .filter_by(id=id)
        )
        result = await session.execute(query)
        return result.unique().scalar_one_or_none()
    

    @classmethod
    async def update_student_with_course(cls, session: AsyncSession, student_id: uuid.UUID, **values) -> Student:
        # Extract courses payload from values, defaulting to empty list when missing/None
        course_data = values.pop("courses", None or [])

        # Load student with existing courses
        student = await session.get(Student, student_id, options=(selectinload(Student.courses),))
        if not student:
            raise ValueError(f"Студент с id {student_id} не найден")

        student.name = values.get("name", student.name)

        student.courses.clear()
        if course_data:
            student.courses.extend([Course(**course) for course in course_data])

        await session.commit()
        await session.refresh(student)
        await session.refresh(student, attribute_names=["courses"])
        return student
    
        
   