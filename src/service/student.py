import uuid
import ujson
import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.redis import RedisClient

from src.schemas.student import SStudentCreate, SStudentRead, SStudentUpdate
from src.repositories.course import CourseRepository

from src.exception.client_exception import NotFoundError
from src.exception.server_exception import InternalServerError

from src.repositories.students import StudentRepository

logger = logging.getLogger(__name__)




class StudentService:
    def __init__(self, session: AsyncSession, repository: StudentRepository, cache: RedisClient, course_repository: CourseRepository):
        self.session = session
        self.cache = cache
        self.repository = repository
        self.course_repository = course_repository

    async def add_student(
        self,student_data: SStudentCreate
    ) -> SStudentRead:
        student, courses = await self.repository.created(student_data)
        if not student:
            logger.error(f"Ошибка при создании студента")
            raise InternalServerError(detail="Ошибка при создании студента")

        courses_data = await self.course_repository.update(courses)
        student.courses = courses_data

        self.session.add(student)
        await self.session.flush()
        await self.session.refresh(student, attribute_names=["courses"])

        student_read_data = SStudentRead.model_validate(student, from_attributes=True)

        cache_key = f"student:{student.id}"
        await self.cache.set(cache_key, student_read_data.model_dump_json())

        return student_read_data


    async def find_all_students(
        self, skip: int = 0, limit: int = 100, **filter_by
    ) -> List[SStudentRead]:
        cache_key = f"students:{filter_by, skip, limit}"
        cached_students = await self.cache.get(cache_key)
        if cached_students:
            return [
                SStudentRead.model_validate_json(student_json)
                for student_json in ujson.loads(cached_students)
            ]

        student_orm = await self.repository.get_all(skip, limit, **filter_by)
        if not student_orm:
            logger.error(f"Не нашло ни одного студента")
            raise NotFoundError(detail="Студенты не найдены")

        students_json = ujson.dumps(
            [
                SStudentRead.model_validate(rec, from_attributes=True).model_dump_json()
                for rec in student_orm
            ]
        )
        await self.cache.set(cache_key, students_json)

        return [
            SStudentRead.model_validate(student_orm, from_attributes=True)
            for student_orm in student_orm
        ]


    async def find_one_with_id(
        self, student_id: uuid.UUID
    ) -> SStudentRead:
        cache_key = f"student:{student_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            student_data = SStudentRead.model_validate_json(cached)

        student_orm = await self.repository.get_id(student_id)
        if not student_orm:
            logger.error(f"Студент с id {student_id} не найден")
            raise NotFoundError(detail=f"Студент с id {student_id} не найден")
        student_data = SStudentRead.model_validate(student_orm, from_attributes=True)

        await self.cache.set(cache_key, student_data.model_dump_json())
        return student_data


    async def update_student_with_course(
        self,
        student_id: uuid.UUID,
        student_data: SStudentUpdate,
    ) -> SStudentRead:
        student = await self.repository.update(student_id, student_data)
        if not student:
            logger.error(f"Ошибка при обновлении студента")
            raise InternalServerError(detail="Ошибка при обновлении студента")

        await self.course_repository.update(student_data.courses)
        student.courses = [course.to_orm_model() for course in student_data.courses]

        await self.session.flush()
        await self.session.refresh(student, attribute_names=["courses"])

        cache_key = f"student:{student_id}"
        await self.cache.set(cache_key, SStudentRead.model_validate(student, from_attributes=True).model_dump_json())

        return SStudentRead.model_validate(student, from_attributes=True)


    async def delete_student(self, **filter_by):
        student = await self.repository.get_id(**filter_by)
        if not student:
            logger.error(f"Ошибка при удалении записи из базы данных")
            raise NotFoundError(student_id=filter_by)

        await self.session.delete(student)

        await self.cache.delete(f"student:{filter_by}")
        return f"Студент с id {filter_by} успешно удалён"
