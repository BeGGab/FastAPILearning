import re
import uuid
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    model_validator,
)
from typing import Optional, List

from src.models.student_models import Student
from src.models.courses_model import Course
from src.schemas.courses_schemas import SCourseCreate, SCourseRead
from src.exception.client_exception import ValidationError, NotFoundError




class SStudentCreate(BaseModel):
    name: str = Field(..., min_length=2, description="Имя студента")
    courses: List[SCourseCreate] = Field(
        default_factory=list, description="Список курсов студента"
    )
    model_config = ConfigDict(from_attributes=True)

    @field_validator("name", mode="before")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if v is None or v == "string":
            raise ValidationError(error="", detail=f"Имя не должно быть пустым")
        return v


    def to_orm_models(self) -> tuple[Student, List[SCourseCreate]]:
        student_data = self.model_dump(exclude="courses")
        student = Student(**student_data)
        return student, self.courses


class SStudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, description="Имя студента")
    courses: Optional[List[SCourseCreate]] = Field(
        None, description="Список курсов студента"
    )
    model_config = ConfigDict(from_attributes=True)

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if isinstance(value, int):
            return str(value)
        elif isinstance(value, str):
            return value
        else:
            raise ValidationError


    @model_validator(mode="after")
    def validate_update_data(self) -> "SStudentUpdate":
        update_fields = self.model_dump(exclude_unset=True, exclude_none=True)
        if not update_fields:
            raise NotFoundError("Нет данных для обновления")
        return self

    async def apply_updates(self, student: Student) -> None:
        for field, value in self.model_dump(
            exclude_unset=True, exclude_none=True, exclude={"courses"}
        ).items():
            setattr(student, field, value)
            

        


class SStudentRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID студента")
    name: str
    courses: List[SCourseRead]

    model_config = ConfigDict(from_attributes=True)
