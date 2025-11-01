import uuid
from typing import List
from sqlalchemy import select, update, delete, event, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
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
        course_data = values.pop("courses", [])
        student = await cls.find_one_with_id(session=session, id=student_id)
        if not student:
            raise ValueError(f"Студент с id {student_id} не найден")
        update_student = (update(cls.model)
                          .where(cls.model.id == student_id)
                          .values(**values)
                          .execution_options(synchronize_session="fetch"))
        if course_data:
            update_courses = (update(Course)
                          .where(Course.id == student_id)
                          .values(**course_data)
                          .execution_options(synchronize_session="fetch"))
            await session.execute(update_courses)
        await session.execute(update_student)
        await session.commit()
        return student 
        
        