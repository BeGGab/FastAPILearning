import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.student import SStudentCreate, SStudentUpdate

from src.models.student import Student

#from src.repositories.course import update as update_courses
from src.repositories.course import update as update_courses






async def create(session: AsyncSession, student_data: SStudentCreate) -> Student:
    student, courses = student_data.to_orm_models()
    if courses:
        courses_data = await update_courses(session, courses)
        student.courses = courses_data
    session.add(student)
    await session.flush()
    return student

async def get_id(session: AsyncSession, student_id: uuid.UUID) -> Optional[Student]:
    query = select(Student).options(joinedload(Student.courses)).filter_by(id=student_id)
    result = await session.execute(query)
    return result.unique().scalar()

async def get_all(session: AsyncSession, **filter_by) -> List[Student]:
    query = select(Student).options(joinedload(Student.courses)).filter_by(**filter_by)
    result = await session.execute(query)
    return result.unique().scalars().all()

async def update(session: AsyncSession, student_id: uuid.UUID, student_data: SStudentUpdate) -> Student:
    student = await get_id(session, student_id)
    student_data.apply_updates(student)
    if student_data.courses is not None:
        await update_courses(session, student_data.courses)
        student.courses = [course.to_orm_model() for course in student_data.courses]
    await session.flush()
    return student

async def delete(session: AsyncSession, student_id: uuid.UUID):
    student = await get_id(session, student_id)
    await session.delete(student)