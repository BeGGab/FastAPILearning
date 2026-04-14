import uuid
import ujson
import logging
import redress 
from typing import List, Any
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.redis import RedisDep

from src.core.config import Settings

from src.schemas.student import SStudentCreate, SStudentRead, SStudentUpdate
from src.repositories.course import CourseRepository as rep_courses
from src.service.courses import delete_courses

from src.exception.client_exception import ValidationError, NotFoundError

from src.repositories.students import StudentRepository as rep_student

logger = logging.getLogger(__name__)

settings = Settings()



class StudentService:
    def __init__(self, session: AsyncSession, redis: RedisDep):
        self.session = session
        self.redis = redis

    @redress.retry(max_attempts=3, deadline_s=10, strategy=redress.strategies.decorrelated_jitter(max_s=5.0))
    async def set_cache(self, key: str, value: Any, ttl: int):
        await self.redis.setex(key, ttl, value)

    async def add_student(
        self,student_data: SStudentCreate
    ) -> SStudentRead:
        student, courses = await rep_student(self.session).created(student_data)
        if not student:
            logger.error(f"Ошибка при создании студента")
            raise ValidationError(detail="Ошибка при создании студента")

        courses_data = await rep_courses(self.session).update(courses)
        student.courses = courses_data

        self.session.add(student)
        await self.session.flush()
        await self.session.refresh(student, attribute_names=["courses"])

        student_read_data = SStudentRead.model_validate(student, from_attributes=True)

        cache_key = f"student:{student.id}"
        await self.set_cache(cache_key, student_read_data.model_dump_json(), settings.ttl)

        return student_read_data


    async def find_all_students(
        self, skip: int = 0, limit: int = 100, **filter_by
    ) -> List[SStudentRead]:
        cache_key = f"students:{filter_by, skip, limit}"
        cached_students = await self.redis.get(cache_key)
        if cached_students:
            return [
                SStudentRead.model_validate_json(student_json)
                for student_json in ujson.loads(cached_students)
            ]

        student_orm = await rep_student(self.session).get_all(skip, limit, **filter_by)
        if not student_orm:
            logger.error(f"Не нашло ни одного студента")
            raise NotFoundError(detail="Студенты не найдены")

        students_json = ujson.dumps(
            [
                SStudentRead.model_validate(rec, from_attributes=True).model_dump_json()
                for rec in student_orm
            ]
        )
        await self.set_cache(cache_key, students_json, settings.ttl)

        return [
            SStudentRead.model_validate(student_orm, from_attributes=True)
            for student_orm in student_orm
        ]


    async def find_one_with_id(
        self, student_id: uuid.UUID
    ) -> SStudentRead:
        cache_key = f"student:{student_id}"
        cached = await self.redis.get(cache_key)
        if cached:
            student_data = SStudentRead.model_validate_json(cached)

        student_orm = await rep_student(self.session).get_id(student_id)
        if not student_orm:
            logger.error(f"Студент с id {student_id} не найден")
            raise NotFoundError(detail=f"Студент с id {student_id} не найден")
        student_data = SStudentRead.model_validate(student_orm, from_attributes=True)

        await self.set_cache(cache_key, student_data.model_dump_json(), settings.ttl)
        return student_data


    async def update_student_with_course(
        self,
        student_id: uuid.UUID,
        student_data: SStudentUpdate,
    ) -> SStudentRead:
        student = await rep_student(self.session).update(student_id, student_data)
        if not student:
            logger.error(f"Ошибка при обновлении студента")
            raise ValidationError(detail="Ошибка при обновлении студента")

        await rep_courses(self.session).update(student_data.courses)
        student.courses = [course.to_orm_model() for course in student_data.courses]

        await self.session.flush()
        await self.session.refresh(student, attribute_names=["courses"])

        cache_key = f"student:{student_id}"
        await self.set_cache(cache_key, SStudentRead.model_validate(student, from_attributes=True).model_dump_json(), settings.ttl)

        return SStudentRead.model_validate(student, from_attributes=True)


    async def delete_student(self, **filter_by):
        student = await rep_student(self.session).get_id(**filter_by)
        if not student:
            logger.error(f"Ошибка при удалении записи из базы данных")
            raise NotFoundError(student_id=filter_by)

        await self.session.delete(student)

        await self.redis.delete(f"student:{filter_by}")
        return f"Студент с id {filter_by} успешно удалён"
