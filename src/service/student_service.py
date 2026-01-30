import uuid
import logging
from typing import List
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.student_schemas import SStudentCreate, SStudentRead, SStudentUpdate
from src.models.student_models import Student
from src.service.courses_service import update_courses
from src.exception.client_exception import BadRequestError
from src.exception.business import StudentNotFoundError



logger = logging.getLogger(__name__)


async def get_student_by_id(session: AsyncSession, student_id: uuid.UUID) -> Student:
    query = (
        select(Student).options(joinedload(Student.courses)).filter_by(id=student_id)
    )
    result = await session.execute(query)
    student = result.scalar()
    if not student:
        logger.error(f"Студент с id {student_id} не найден")
        raise StudentNotFoundError(student_id=student_id)
    return student


async def add_student(
    session: AsyncSession, student_data: SStudentCreate
) -> SStudentRead:
    try:
        student, courses = student_data.to_orm_models()
        student.courses = await update_courses(session, student_data.courses)

        session.add(student)
        await session.flush()
        await session.refresh(student, ["courses"])
        return SStudentRead.model_validate(student, from_attributes=True)
    except IntegrityError as e:
        raise BadRequestError(detail=str(e))


async def find_all_students(session: AsyncSession, **filter_by) -> List[SStudentRead]:
    query = select(Student).options(joinedload(Student.courses)).filter_by(**filter_by)
    result = await session.execute(query)
    record = list(result.unique().scalars().all())
    if not record:
        logger.warning(f"Студенты с параметрами {filter_by} не найдены, возвращен пустой список.")
        raise StudentNotFoundError(detail=f"Студенты с параметрами {filter_by} не найдены")
    return [SStudentRead.model_validate(rec, from_attributes=True) for rec in record]


async def find_one_with_id(session: AsyncSession, student_id: uuid.UUID) -> SStudentRead:
    query = select(Student).options(joinedload(Student.courses)).filter_by(id=student_id)
    result = await session.execute(query)
    record = result.scalar()
    if not record:
        logger.error(f"Студент с id {student_id} не найден")
        raise StudentNotFoundError(student_id=student_id)
    return SStudentRead.model_validate(record, from_attributes=True)


async def update_student_with_course(
    session: AsyncSession, student_id: uuid.UUID, student_data: SStudentUpdate
) -> SStudentRead:
    student = await get_student_by_id(session=session, student_id=student_id)
    if not student:
        logger.error(f"Ошибка при поиске записи в базе данных")
        raise StudentNotFoundError(student_id=student_id)
    try:
        update_data = student_data.model_dump(exclude_unset=True)

        if "name" in update_data:
            student.name = update_data["name"]
        if "courses" in update_data:
            student.courses = await update_courses(session, student_data.courses)

        await session.flush()
        await session.refresh(student, attribute_names=["courses"])
        return SStudentRead.model_validate(student, from_attributes=True)
    except IntegrityError as e:
        raise BadRequestError(detail=str(e))




async def delete_student(session: AsyncSession, student_id: uuid.UUID):
    student = await get_student_by_id(session, student_id=student_id)
    if not student:
        logger.error(f"Ошибка при удалении записи из базы данных")
        raise StudentNotFoundError(student_id=student_id)
    await session.delete(student)
    return f"Студент с id {student_id} успешно удалён"
