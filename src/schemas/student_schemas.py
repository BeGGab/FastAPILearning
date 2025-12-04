import re
import uuid
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import Optional, List, Dict, Any

from src.models.student_models import Course


class SCourseCreate(BaseModel):
    title: str = Field(..., min_length=1)

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Название курса не может быть пустым")
        return value


class SCourseRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID курса")
    title: str

    model_config = ConfigDict(from_attributes=True)


class SStudentCreate(BaseModel):
    name: str = Field(..., min_length=2, description="Имя студента")
    courses: List[SCourseCreate] = Field(
        default_factory=list, description="Список курсов студента"
    )

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, value: str) -> str:
        if value and len(value.strip()) < 2:
            raise ValueError("Имя студента должно содержать хотя бы 2 символа")
        return value

    def prepare_db_data(self) -> dict:
        student_data = self.model_dump(exclude={"courses"})
        student_data["courses"] = [
            Course(**course.model_dump()) for course in self.courses
        ]
        return student_data


class SStudentRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID студента")
    name: str
    courses: List[SCourseRead]

    model_config = ConfigDict(from_attributes=True)
