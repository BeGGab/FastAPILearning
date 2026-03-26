import uuid
import json
import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import RedisDep

from src.client.bio_student_client import StudentServiceClient, get_student_client

from redress import CircuitOpenError

from src.schemas.student import SStudentCreate, SStudentRead, SStudentUpdate
from src.repositories.course import CourseRepository as rep_courses
from src.service.courses import delete_courses

from src.exception.client_exception import ValidationError, NotFoundError

from src.repositories.students import StudentRepository as rep_student


logger = logging.getLogger(__name__)


async def add_student(
    session: AsyncSession, redis: RedisDep, student_data: SStudentCreate, student_client: StudentServiceClient
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

    student_read_data = SStudentRead.model_validate(student, from_attributes=True)
    try:
        bio_data = await student_client.get_student(student_id=student.id)
        student_read_data = rep_student(session).apply_bio_data_to_student(
            student_read_data, bio_data
        )
    except CircuitOpenError:
        logger.warning(
            f"Circuit Breaker для сервиса биографий открыт. Запрос для студента {student.id} не выполнен."
        )

    cache_key = f"student:{student.id}"
    try:
        await redis.delete(cache_key)
        await redis.setex(
            cache_key,
            3600,
            student_read_data.model_dump_json(),
        )
    except Exception as e:
        logger.warning(
            f"Не удалось обновить кэш после создания студента {student.id}: {e}"
        )

    return student_read_data


async def find_all_students(
    session: AsyncSession, redis: RedisDep, skip: int = 0, limit: int = 100, **filter_by
) -> List[SStudentRead]:
    cache_key = f"students:{filter_by, skip, limit}"
    cached_students = await redis.get(cache_key)
    if cached_students:
        return [
            SStudentRead.model_validate_json(student_json)
            for student_json in json.loads(cached_students)
        ]

    student_orm = await rep_student(session).get_all(skip, limit, **filter_by)
    if not student_orm:
        logger.error(f"Не нашло ни одного студента")
        raise NotFoundError(detail="Студенты не найдены")

    try:
        students_json = json.dumps(
            [
                SStudentRead.model_validate(rec, from_attributes=True).model_dump_json()
                for rec in student_orm
            ]
        )
        await redis.setex(cache_key, 3600, students_json)
    except Exception as e:
        logger.warning(f"Не удалось записать студентов в кэш: {e}")

    return [
        SStudentRead.model_validate(student_orm, from_attributes=True)
        for student_orm in student_orm
    ]


async def find_one_with_id(
    session: AsyncSession, redis: RedisDep, student_id: uuid.UUID, student_client: StudentServiceClient
) -> SStudentRead:
    cache_key = f"student:{student_id}"
    cached = await redis.get(cache_key)
    if cached:
        student_data = SStudentRead.model_validate_json(cached)
        try:
            bio_data = await student_client.get_student(student_id=student_id)
            enriched_student = rep_student(session).apply_bio_data_to_student(
                student_data, bio_data
            )
            if enriched_student.model_dump() != student_data.model_dump():
                await redis.setex(cache_key, 3600, enriched_student.model_dump_json())

            return enriched_student
        except CircuitOpenError:
            logger.warning(
                f"Circuit Breaker для сервиса биографий открыт. Запрос для студента {student_id} не выполнен."
            )
            return student_data
        except Exception as e:
            logger.warning(
                f"Не удалось дообогатить студента {student_id} из сервиса биографий: {e}"
            )
            return student_data

    student_orm = await rep_student(session).get_id(student_id)
    if not student_orm:
        logger.error(f"Студент с id {student_id} не найден")
        raise NotFoundError(detail=f"Студент с id {student_id} не найден")
    student_data = SStudentRead.model_validate(student_orm, from_attributes=True)
    try:
        bio_data = await student_client.get_student(student_id=student_id)
        student_data = rep_student(session).apply_bio_data_to_student(
            student_data, bio_data
        )
    except CircuitOpenError:
        logger.warning(
            f"Circuit Breaker для сервиса биографий открыт. Запрос для студента {student_id} не выполнен."
        )
    except Exception as e:
        logger.warning(
            f"Не удалось дообогатить студента {student_id} из сервиса биографий: {e}"
        )

    try:
        await redis.setex(
            cache_key,
            3600,
            student_data.model_dump_json(),
        )
    except Exception as e:
        logger.warning(f"Не удалось записать студента {student_id} в кэш: {e}")
    return student_data


async def update_student_with_course(
    session: AsyncSession,
    redis: RedisDep,
    student_id: uuid.UUID,
    student_data: SStudentUpdate,
) -> SStudentRead:
    student = await rep_student(session).update(student_id, student_data)
    if not student:
        logger.error(f"Ошибка при обновлении студента")
        raise ValidationError(detail="Ошибка при обновлении студента")

    await rep_courses(session).update(student_data.courses)
    student.courses = [course.to_orm_model() for course in student_data.courses]

    await session.flush()
    await session.refresh(student, attribute_names=["courses"])

    cache_key = f"student:{student_id}"
    try:
        await redis.delete(cache_key)
        await redis.setex(
            cache_key,
            3600,
            SStudentRead.model_validate(
                student, from_attributes=True
            ).model_dump_json(),
        )
    except Exception as e:
        logger.warning(
            f"Не удалось обновить кэш после изменения студента {student_id}: {e}"
        )

    return SStudentRead.model_validate(student, from_attributes=True)


async def delete_student(session: AsyncSession, redis: RedisDep, **filter_by):
    student = await rep_student(session).get_id(**filter_by)
    if not student:
        logger.error(f"Ошибка при удалении записи из базы данных")
        raise NotFoundError(student_id=filter_by)

    await session.delete(student)

    try:
        await redis.delete(f"student:{filter_by}")
    except Exception as e:
        logger.warning(f"Не удалось удалить ключ кэша студента {filter_by}: {e}")
    return f"Студент с id {filter_by} успешно удалён"
