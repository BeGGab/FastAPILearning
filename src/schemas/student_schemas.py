import re
import uuid
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import Optional, List, Dict, Any

from src.models.courses_model import Course
from src.schemas.courses_schemas import SCourseCreate, SCourseRead


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


class SStudentRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID студента")
    name: str
    courses: List[SCourseRead]

    model_config = ConfigDict(from_attributes=True)
