import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.student import Student

from src.schemas.student import SStudentCreate, SStudentUpdate, SStudentRead


class StudentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def created(self, student_data: SStudentCreate) -> Student:
        student, courses = student_data.to_orm_models()
        return student, courses

    async def get_id(self, student_id: uuid.UUID) -> Optional[Student]:
        query = (
            select(Student)
            .options(joinedload(Student.courses))
            .filter_by(id=student_id)
        )
        result = await self.session.execute(query)
        return result.unique().scalar()

    async def get_all(
        self, skip: int = 0, limit: int = 100, **filter_by
    ) -> List[Student]:
        query = (
            select(Student)
            .options(joinedload(Student.courses))
            .filter_by(**filter_by)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def update(
        self, student_id: uuid.UUID, student_data: SStudentUpdate
    ) -> Student:
        student = await self.get_id(student_id)

        student_data.apply_updates(student)

        return student

    def apply_bio_data_to_student(
        self, student_data: SStudentRead, bio_data: Optional[dict]
    ) -> SStudentRead:
        if not bio_data:
            return student_data
        return student_data.model_copy(
            update={
                "email": bio_data.get("email"),
                "phone_number": bio_data.get("phone_number"),
                "bio_text": bio_data.get("text"),
                "year_of_enrollment": bio_data.get("year_of_enrollment"),
                "year_of_graduation": bio_data.get("year_of_graduation"),
            }
        )
