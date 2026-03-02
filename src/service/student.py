import uuid
import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.student import SStudentCreate, SStudentRead, SStudentUpdate
from src.repositories.course import CourseRepository as rep_courses
from src.service.courses import delete_courses

from src.exception.client_exception import ValidationError, NotFoundError

from src.repositories.students import StudentRepository as rep_student


logger = logging.getLogger(__name__)


async def add_student(
    session: AsyncSession, student_data: SStudentCreate
) -> SStudentRead:
    student, courses = await rep_student(session).created(student_data)
    if not student:
        logger.error(f"Ошибка при создании студента")
        raise ValidationError(detail="Ошибка при создании студента")

    courses_data = await rep_courses(session).update(courses)
    student.courses = courses_data

    session.add(student)
    await session.flush()
    await session.refresh(student, attribute_names=["courses"])
    return SStudentRead.model_validate(student, from_attributes=True)


async def find_all_students(
    session: AsyncSession, skip: int = 0, limit: int = 100, **filter_by
) -> List[SStudentRead]:
    student_orm = await rep_student(session).get_all(skip, limit, **filter_by)
    if not student_orm:
        logger.error(f"Не нашло ни одного студента")
        raise NotFoundError(detail="Студенты не найдены")

    return [
        SStudentRead.model_validate(student_orm, from_attributes=True)
        for student_orm in student_orm
    ]


async def find_one_with_id(
    session: AsyncSession, student_id: uuid.UUID
) -> SStudentRead:
    student_orm = await rep_student(session).get_id(student_id)
    if not student_orm:
        logger.error(f"Студент с id {student_id} не найден")
        raise NotFoundError(student_id=student_id)
    return SStudentRead.model_validate(student_orm, from_attributes=True)


async def update_student_with_course(
    session: AsyncSession, student_id: uuid.UUID, student_data: SStudentUpdate
) -> SStudentRead:
    student = await rep_student(session).update(student_id, student_data)
    if not student:
        logger.error(f"Ошибка при обновлении студента")
        raise ValidationError(detail="Ошибка при обновлении студента")

    await rep_courses(session).update(student_data.courses)
    student.courses = [course.to_orm_model() for course in student_data.courses]

    await session.flush()
    await session.refresh(student, attribute_names=["courses"])
    return SStudentRead.model_validate(student, from_attributes=True)


async def delete_student(session: AsyncSession, **filter_by):
    student = await rep_student(session).get_id(**filter_by)
    if not student:
        logger.error(f"Ошибка при удалении записи из базы данных")
        raise NotFoundError(student_id=filter_by)
    return f"Студент с id {filter_by} успешно удалён"
