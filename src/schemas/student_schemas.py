import re
import uuid
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator, model_validator
from typing import Optional, List, Dict, Any

from src.models.student_models import Student
from src.models.courses_model import Course
from src.schemas.courses_schemas import SCourseCreate, SCourseRead


class SStudentCreate(BaseModel):
    name: str = Field(..., min_length=2, description="Имя студента")
    courses: List[SCourseCreate] = Field(
        default_factory=list, description="Список курсов студента"
    )

    @field_validator("name", mode="before")
    @classmethod
    def name_not_empty(cls, value: str) -> str:
        if isinstance(value, str):
            return value
        elif isinstance(value, int):
            return str(value)
        else:
            raise ValueError("Имя должно быть строкой или числом")

    @model_validator(mode="after")
    def set_default_name(self):
        if self.name is None or self.name == "string":
            self.name = f"Student_{str(uuid.uuid4())[:8]}"
        return self
    
    @model_validator(mode="after")
    def validate_courses(self) -> "SStudentCreate":
        if self.courses is None:
            return self
        return self
    
    def to_orm_models(self) -> tuple[Student, List[Course]]:
        student_data = self.model_dump(exclude="courses")
        student = Student(**student_data)
        return student, self.courses



class SStudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, description="Имя студента")
    courses: Optional[List[SCourseCreate]] = Field(None, description="Список курсов студента")



class SStudentRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID студента")
    name: str
    courses: List[SCourseRead]

    model_config = ConfigDict(from_attributes=True)
