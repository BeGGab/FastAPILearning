import uuid
import logger
from typing import List
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.student_schemas import SStudentCreate, SCourseCreate
from src.models.student_models import Student, Course, student_course
from src.service.courses_service import (find_existing_courses, create_new_courses, find_or_create_courses)
from src.dao.base import BaseDAO


async def add_student(session: AsyncSession, student_data: SStudentCreate) -> Student:
    try:
        student_dict = student_data.model_dump()

        student_dict.pop("courses", None)
        student = Student(**student_dict)
        student.courses = await find_or_create_courses(session, student_data.courses)

        session.add(student)
        logger.logger.info(f"Запись {student.name} успешно добавлена в базу данных")
        await session.flush()
        await session.refresh(student, ["courses"])
        return student
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при добавлении записи в базу данных: {e}")
        raise


async def find_all_students(session: AsyncSession, **filter_by) -> List[Student]:
    try:
        query = (
            select(Student).options(joinedload(Student.courses)).filter_by(**filter_by)
        )
        result = await session.execute(query)
        record = list(result.unique().scalars().all())
        logger.logger.info(f"Записи {len(record)} успешно найдены в базе данных")
        return list(record)
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при поиске записей в базе данных: {e}")
        raise


async def find_one_with_id(session: AsyncSession, id: uuid.UUID) -> Student:
    try:
        query = select(Student).options(joinedload(Student.courses)).filter_by(id=id)
        result = await session.execute(query)
        record = result.scalar()
        logger.logger.info(f"Запись {record.name} успешно найдена в базе данных")
        return record
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при поиске записи в базе данных: {e}")
        raise


async def update_student_with_course(
    session: AsyncSession, student_id: uuid.UUID, student_data: SStudentCreate
) -> Student:
    student = await find_one_with_id(session=session, id=student_id)
    logger.logger.info(f"Запись {student.name} успешно найдена в базе данных")
    if not student:
        raise ValueError(f"Студент с id {student_id} не найден")
    try:
        student.name = student_data.name
        student.courses = await find_or_create_courses(session, student_data.courses)
        logger.logger.info(f"Запись {student.name} успешно обновлена в базе данных")
        await session.refresh(student, attribute_names=["courses"])
        return student
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при обновлении записи в базе данных: {e}")
        raise


async def delete_student(session: AsyncSession, student_id: uuid.UUID):
    student = await find_one_with_id(session, id=student_id)
    logger.logger.info(f"Запись {student.name} успешно найдена в базе данных")
    if not student:
        raise ValueError(f"Студент с id {student_id} не найден")
    try:
        await session.delete(student)
        logger.logger.info(f"Запись {student.name} успешно удалена из базы данных")
        return student
    except SQLAlchemyError as e:
        logger.logger.error(f"Ошибка при удалении записи из базы данных: {e}")
        raise
